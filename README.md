# Server API

Serverless Python API built on AWS Lambda, packaged as a Docker image, and deployed with the Serverless Framework.

The project exposes both HTTP endpoints and asynchronous event-driven flows for meal processing:

- **POST `/signin`** – login
- **POST `/signup`** – signup
- **GET `/me`** – authenticated user data
- **POST `/meals`** – create authenticated meal
- **GET `/meals`** – list authenticated meals
- **GET `/meals/{meal_id}`** – authenticated meal detail

There are also two event-driven functions:

- **`fileUploadEvent`** – triggered by S3 uploads and sends a message to SQS
- **`processMeal`** – SQS consumer that processes the uploaded file and persists the meal

---

## Stack

- **Language:** Python 3.11
- **Runtime:** `public.ecr.aws/lambda/python:3.11`
- **Serverless Framework** (deploys to AWS Lambda + API Gateway HTTP API)
- **Infrastructure:** AWS Lambda + API Gateway HTTP API + S3 + SQS
- **Database:** configured via environment variable `DATA_BASE_URL`
- **Auth:** JWT (keys configured via `SECRET_JWT_PRIVATE_KEY` and `SECRET_JWT_PUBLIC_KEY`)
- **OpenAI:** `OPENAI_API_KEY` for meal processing AI integration
- **Migrations:** Alembic (`alembic/`)

---

## Architecture

Main directories:

- **`src/functions/`**
  - `signin.py` – login Lambda handler
  - `signup.py` – signup Lambda handler
  - `me.py` – authenticated user Lambda handler
  - `create_meal.py` – meal creation Lambda handler
  - `list_meals.py` – meal listing Lambda handler
  - `get_meal_by_id.py` – meal detail Lambda handler
  - `file_upload_event.py` – S3-triggered Lambda handler
  - `process_meal.py` – SQS-triggered Lambda handler

- **`src/controllers/`**
  - Controllers containing business logic for each endpoint and workflow

- **`src/utils/`**
  - `parse_event.py`, `parse_protected_event.py` – parse API Gateway events and authentication
  - `parse_response.py` – convert responses to API Gateway format
  - `http.py` – HTTP helpers and error responses

- **`src/services/`**
  - `ai.py` – OpenAI client
  - `storage.py` – S3 integration
  - `hashed_service.py` – password hashing

- **`src/repository/`**
  - `meal_repository.py`, `user_repository.py` – data access

- **`src/lib/`**
  - `jwt.py`, `generate_keys.py` – JWT utilities

- **`alembic/` + `alembic.ini`**
  - database configuration and migrations

---

## Lambda Flow

### HTTP API

The following functions are exposed via API Gateway HTTP API:

- `signin` → `POST /signin`
- `signup` → `POST /signup`
- `me` → `GET /me`
- `createMeal` → `POST /meals`
- `listMeals` → `GET /meals`
- `getMealById` → `GET /meals/{meal_id}`

Protected routes use `parse_protected_event` to validate the `Authorization: Bearer <token_jwt>` token.

### Asynchronous events

- `fileUploadEvent` is triggered when a new object is created in the S3 bucket `UploadsBucket`.
- It sends a message to the SQS queue `MealsQueue` with the uploaded object `file_key`.
- `processMeal` consumes messages from `MealsQueue`, loads the file, processes the meal with AI, and persists the result.

---

## Serverless Lambda Handlers

Each Lambda function defines a synchronous `handler` that calls an internal `async_handler`:

- `src.functions.signin.handler`
- `src.functions.signup.handler`
- `src.functions.me.handler`
- `src.functions.create_meal.handler`
- `src.functions.list_meals.handler`
- `src.functions.get_meal_by_id.handler`
- `src.functions.file_upload_event.handler`
- `src.functions.process_meal.handler`

In `serverless.yml`, the image command is configured like this:

```yaml
functions:
  signin:
    image:
      uri: ${env:ECR_IMAGE_URI}
      command:
        - src.functions.signin.handler
  signup:
    image:
      uri: ${env:ECR_IMAGE_URI}
      command:
        - src.functions.signup.handler
  me:
    image:
      uri: ${env:ECR_IMAGE_URI}
      command:
        - src.functions.me.handler
  createMeal:
    image:
      uri: ${env:ECR_IMAGE_URI}
      command:
        - src.functions.create_meal.handler
  listMeals:
    image:
      uri: ${env:ECR_IMAGE_URI}
      command:
        - src.functions.list_meals.handler
  getMealById:
    image:
      uri: ${env:ECR_IMAGE_URI}
      command:
        - src.functions.get_meal_by_id.handler
  fileUploadEvent:
    image:
      uri: ${env:ECR_IMAGE_URI}
      command:
        - src.functions.file_upload_event.handler
  processMeal:
    image:
      uri: ${env:ECR_IMAGE_URI}
      command:
        - src.functions.process_meal.handler
```

---

## Environment Variables

Defined in `serverless.yml`:

- **`DATA_BASE_URL`** – database connection URL
- **`SECRET_JWT_PRIVATE_KEY`** – JWT private key
- **`SECRET_JWT_PUBLIC_KEY`** – JWT public key
- **`OPENAI_API_KEY`** – OpenAI API key for meal processing
- **`BUCKET_NAME`** – S3 uploads bucket name
- **`MEALS_QUEUE_URL`** – SQS queue URL used by `fileUploadEvent`
- **`ECR_IMAGE_URI`** – Docker image URI stored in ECR

---

## Docker

The base image is defined in `Dockerfile`:

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target ${LAMBDA_TASK_ROOT}
COPY src/ ${LAMBDA_TASK_ROOT}/src/
```

### Build the image

```bash
docker buildx build --platform linux/amd64 --provenance=false -t lambda-container:latest .
```

### Push to ECR

```bash
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag lambda-container:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/lambda-container:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/lambda-container:latest
```

---

## Serverless Framework

### Requirements

- Node.js + npm/yarn
- Serverless Framework installed globally:

```bash
npm install -g serverless
```

- AWS CLI configured (`aws configure`) with valid credentials.

### Deploy

```bash
serverless deploy
```

This command will create or update the Lambda functions and required resources:

- HTTP functions: `signin`, `signup`, `me`, `createMeal`, `listMeals`, `getMealById`
- event functions: `fileUploadEvent`, `processMeal`
- resources: S3 bucket `UploadsBucket`, SQS queue `MealsQueue`, DLQ `MealsDLQ`

---

## Endpoints

### `POST /signup`

- **Description:** Creates a new user.
- **Body (JSON):** `email`, `password`, etc.
- **Response:** created user data and/or a JWT token.

### `POST /signin`

- **Description:** Authenticates a user.
- **Body (JSON):** `email`, `password`.
- **Response:** JWT token and basic user information.

### `GET /me`

- **Description:** Returns authenticated user data.
- **Headers:** `Authorization: Bearer <token_jwt>`
- **Response:** `200` with user data or `401` if invalid.

### `POST /meals`

- **Description:** Creates a new authenticated meal.
- **Headers:** `Authorization: Bearer <token_jwt>`
- **Body:** meal creation payload.

### `GET /meals`

- **Description:** Lists authenticated user's meals.
- **Headers:** `Authorization: Bearer <token_jwt>`

### `GET /meals/{meal_id}`

- **Description:** Retrieves details of an authenticated meal.
- **Headers:** `Authorization: Bearer <token_jwt>`
- **Headers:** `Authorization: Bearer <token_jwt>`

---

## Desenvolvimento local

```bash
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
```

Use testes unitários e o código local diretamente para validar a lógica sem precisar rodar Lambda em produção.
