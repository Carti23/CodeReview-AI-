
# 🚀 CodeReviewAI Backend

**CodeReviewAI Backend** is a Python-based prototype for automating the review of coding assignments. By integrating AI-powered code analysis using OpenAI's GPT API (or alternatives) with GitHub repository access, this tool streamlines and enhances the review process.

---

## 🛠️ Getting Started

### 📥 Clone the Repository

Start by cloning the project from GitHub:

```bash
git clone git@github.com:Carti23/CodeReview-AI-.git
cd CodeReview-AI-
```

---

## 🖥️ Deployment Instructions

### Using Docker Compose

1. Build and run the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Verify the application is running at the specified endpoint.

---

## 🛠️ Configuring the Application

Configuration is managed through environment variables, making it easy to adapt the application to different setups. You need to have kesy for (GithubAPI, OpenAI)

---

## 🔧 Features

- **GitHub Integration**: Supports cloning and analyzing repositories, managing large repositories with 100+ files.
- **High Scalability**: Handles over 100 review requests per minute with a distributed architecture.

---

## 🏗️ System Architecture

To scale the system for high traffic and large repositories, the architecture is designed as follows:

### Database Layer
- Use **PostgreSQL** with read replicas and **Redis** for caching frequent queries.
- Employ database sharding for faster data retrieval and write operations.

### Queue Management
- Integrate a message queue system like **RabbitMQ** or **Kafka** to handle asynchronous review requests.

### File Processing
- Utilize parallel processing with tools like **Celery** to handle large repositories and concurrent tasks.

### API Rate Limits
- Cache GitHub repository data with **Redis** to minimize API calls.
- Optimize OpenAI API payloads for efficient usage and consider alternative APIs like **Hugging Face** if necessary.

---

## 📚 Documentation

- **Pydantic Settings**: [Read the documentation](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
- **OpenAI API**: [Read the documentation](https://platform.openai.com/docs/)
- **GitHub API**: [Read the documentation](https://docs.github.com/en/rest)

---

## 🛡️ Security

To ensure secure operations:
- **API Keys**: Store sensitive keys in environment variables or secret managers.
- **Access Control**: Implement role-based access control for users and reviewers.

---

## 🧑‍💻 Contribution Guide

1. Fork the repository.
2. Create a new feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit and push your changes:
   ```bash
   git commit -m "Add your feature"
   git push origin feature/your-feature
   ```
4. Open a pull request.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

---

