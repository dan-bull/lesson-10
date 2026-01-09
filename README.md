# MLOps Train Automation (AWS Step Functions Simulation)

## Опис проєкту

Цей проєкт демонструє побудову MLOps-пайплайну тренування моделі з використанням **AWS Step Functions**, **Lambda** та **Terraform**.

Оскільки реальне підключення до AWS не використовується, у проєкті застосовується **LocalStack** — локальна симуляція AWS-сервісів. Архітектура, Terraform-код та GitLab CI повністю сумісні з реальним AWS і можуть бути використані в продакшені з мінімальними змінами.

---

## Мета

- Створити Step Function із кількох послідовних кроків
- Реалізувати Lambda-функції для етапів пайплайну
- Описати всю інфраструктуру через Terraform
- Налаштувати GitLab CI для автоматичного запуску Step Function при push
- Передавати вхідні параметри через JSON

---

## Архітектура

```

GitLab Push
│
▼
GitLab CI job
│
▼
AWS Step Functions (LocalStack)
│
├── ValidateData (Lambda)
│
└── LogMetrics (Lambda)

```

---

## Структура проєкту

```

mlops-train-automation/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── lambda/
│       ├── validate.py
│       ├── log_metrics.py
│       ├── validate.zip
│       └── log_metrics.zip
├── .gitlab-ci.yml
└── README.md

````

---

## Передумови

Необхідно мати встановлені:

- Docker
- Terraform >= 1.5
- AWS CLI
- LocalStack
- Python 3.9+

Перевірка:

```bash
docker --version
terraform -v
aws --version
localstack --version
````

---

## Lambda-функції

### validate.py

Виконує умовну валідацію даних.

```python
print("Validating data...")
```

### log_metrics.py

Імітує логування метрик після тренування.

```python
print("Logging metrics...")
```

---

## Збірка Lambda ZIP-архівів

Lambda-функції повинні бути зібрані у `.zip` архіви перед запуском Terraform.

```bash
cd terraform/lambda
zip validate.zip validate.py
zip log_metrics.zip log_metrics.py
```
![alt text](<Screenshot 2026-01-09 at 16.54.20.png>)
---

## Запуск LocalStack (симуляція AWS)

LocalStack використовується для імітації AWS Lambda, IAM та Step Functions.

```bash
localstack start
```

LocalStack буде доступний на:

```
http://localhost:4566
```
![alt text](<Screenshot 2026-01-09 at 16.56.28.png>)
---

## Розгортання інфраструктури через Terraform

Terraform **запускається з директорії `terraform/`**.

```bash
cd terraform
terraform init
terraform apply
```

У результаті буде створено:

* IAM ролі для Lambda та Step Functions
* 2 Lambda-функції
* Step Function з двома кроками:

  * `ValidateData`
  * `LogMetrics`
![alt text](<Screenshot 2026-01-09 at 16.54.39.png>)
![alt text](<Screenshot 2026-01-09 at 16.54.49.png>)
![alt text](<Screenshot 2026-01-09 at 16.54.57.png>)
---

## Ручний запуск Step Function

Для перевірки пайплайну вручну використовується AWS CLI з LocalStack.

```bash
awslocal stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-1:000000000000:stateMachine:ml-train-pipeline \
  --name manual-test \
  --input '{"source":"manual","run":"test"}'
```
![alt text](<Screenshot 2026-01-09 at 16.56.34.png>)
---

## GitLab CI

### .gitlab-ci.yml

GitLab CI автоматично запускає Step Function при кожному push.

Основні характеристики:

* Використовується офіційний образ `amazon/aws-cli`
* Викликається `aws stepfunctions start-execution`
* Вхідні параметри передаються через JSON

```yaml
train-model:
  stage: train
  image: amazon/aws-cli:2.15.0
  script:
    - aws stepfunctions start-execution \
        --endpoint-url http://localstack:4566 \
        --state-machine-arn arn:aws:states:us-east-1:000000000000:stateMachine:ml-train-pipeline \
        --name "train-$CI_PIPELINE_ID" \
        --input '{"source":"gitlab-ci","commit":"'"$CI_COMMIT_SHORT_SHA"'"}'
```

---

## Змінні середовища GitLab CI

У реальному AWS необхідно додати такі змінні у GitLab CI Settings:

* `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`
* `AWS_DEFAULT_REGION`

Для LocalStack використовуються тестові значення.

---

## Приклад JSON, що передається у Step Function

```json
{
  "source": "gitlab-ci",
  "commit": "a1b2c3d"
}
```