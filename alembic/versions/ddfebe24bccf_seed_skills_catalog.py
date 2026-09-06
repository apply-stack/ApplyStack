"""seed skills catalog

Revision ID: ddfebe24bccf
Revises: 44628ff10c8b
Create Date: 2026-09-06

Canonical skill catalog. Users pick from these; the LLM job-description
extractor maps whatever wording a posting uses onto these exact names.

Names are written out in full ("JavaScript", not "JS"; "AWS",
not "AWS"). Initialisms that ARE the accepted name are kept as-is - nobody
writes "HyperText Markup Language" or "Representational State Transfer".
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert

from alembic import op

revision: str = "ddfebe24bccf"
down_revision: str | Sequence[str] | None = "44628ff10c8b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# fmt: off
SKILLS: list[str] = [
    # ---------------------------------------------------------- languages
    "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go",
    "Rust", "Kotlin", "Swift", "Ruby", "PHP", "Scala", "R", "MATLAB", "Perl",
    "Dart", "Elixir", "Haskell", "Lua", "Objective-C", "F#", "Julia",
    "Groovy", "Clojure", "Erlang", "Assembly", "Solidity", "Zig", "OCaml",
    "Visual Basic .NET", "Delphi", "COBOL", "Fortran",
    # ------------------------------------------------- markup and scripting
    "HTML", "CSS", "SQL", "Sass", "Less", "XML", "JSON", "YAML", "Markdown",
    "LaTeX", "Regular Expressions", "Bash", "Shell Scripting", "PowerShell",
    "Makefile",
    # ---------------------------------------------------------- frontend
    "React", "Angular", "Vue.js", "Svelte", "SvelteKit", "Next.js", "Nuxt.js",
    "Remix", "Astro", "jQuery", "Redux", "MobX", "Zustand", "React Query",
    "React Router", "Tailwind CSS", "Bootstrap", "Material UI", "Chakra UI",
    "Ant Design", "Styled Components", "Webpack", "Vite", "Rollup", "Babel",
    "ESLint", "Prettier", "Storybook", "Three.js", "D3.js", "Chart.js",
    "Framer Motion", "Electron", "Progressive Web Apps",
    "Responsive Web Design", "Web Accessibility", "Server-Side Rendering",
    "Web Components",
    # ---------------------------------------------------------- backend
    "Node.js", "Deno", "Bun", "Express.js", "NestJS", "Fastify", "Koa",
    "Django", "Django REST Framework", "Flask", "FastAPI", "Tornado",
    "Ruby on Rails", "Sinatra", "Laravel", "Symfony", "CodeIgniter",
    "Spring", "Spring Boot", "Spring Security", "Hibernate", "Micronaut",
    "Quarkus", "Ktor", "ASP.NET Core", "Entity Framework Core", "Blazor",
    "Gin", "Echo", "Fiber", "Actix Web", "Axum", "Rocket", "Phoenix",
    "SQLAlchemy", "Alembic", "Pydantic", "Celery", "Prisma", "TypeORM",
    "Sequelize", "Drizzle ORM", "ORM",
    # ---------------------------------------------------------- mobile
    "Android Development", "iOS Development", "React Native", "Flutter",
    "SwiftUI", "UIKit", "Jetpack Compose", "Kotlin Multiplatform", "Xamarin",
    "Ionic", "Expo", "Mobile Application Development",
    # --------------------------------------------------------- databases
    "PostgreSQL", "MySQL", "MariaDB", "SQLite", "Microsoft SQL Server",
    "Oracle Database", "MongoDB", "Redis", "Apache Cassandra", "Amazon DynamoDB",
    "Elasticsearch", "OpenSearch", "Neo4j", "InfluxDB", "ClickHouse",
    "CockroachDB", "Couchbase", "Firebase Realtime Database", "Cloud Firestore",
    "Supabase", "pgvector", "Pinecone", "Qdrant", "Weaviate", "Milvus",
    "Chroma", "Database Design", "Database Normalization", "Database Indexing",
    "Query Optimization", "Stored Procedures", "Database Migrations",
    "Database Replication", "Database Sharding", "Transaction Management",
    "Vector Databases",
    # ------------------------------------------------------------ cloud
    "AWS", "Azure", "GCP",
    "DigitalOcean", "Heroku", "Vercel", "Netlify", "Cloudflare", "Railway",
    "Fly.io", "AWS Lambda", "Amazon S3", "Amazon EC2", "Amazon RDS",
    "Amazon CloudFront", "Azure Functions", "Azure DevOps",
    "Google Cloud Functions", "Google BigQuery", "Cloud Architecture",
    "Serverless Architecture", "Cloud Cost Optimization", "Multi-Tenancy",
    # --------------------------------------------------- devops and infra
    "Docker", "Docker Compose", "Kubernetes", "Helm", "OpenShift", "Podman",
    "Terraform", "Ansible", "Pulumi", "Vagrant", "Jenkins", "GitHub Actions",
    "GitLab CI", "CircleCI", "Travis CI", "TeamCity", "Argo CD",
    "CI/CD", "Infrastructure as Code",
    "Nginx", "Apache HTTP Server", "Traefik", "HAProxy", "Linux",
    "Unix", "Windows Server", "Systems Administration", "Shell Automation",
    "Prometheus", "Grafana", "Datadog", "New Relic", "Sentry", "ELK Stack",
    "OpenTelemetry", "Logging", "Monitoring", "Observability", "Load Balancing",
    "Site Reliability Engineering", "Capacity Planning", "Disaster Recovery",
    "Secrets Management", "HashiCorp Vault",
    # ------------------------------------------------ messaging and events
    "Apache Kafka", "RabbitMQ", "Apache Pulsar", "Amazon SQS",
    "NATS", "ZeroMQ", "Message Queues", "Event-Driven Architecture",
    "Publish-Subscribe Pattern", "Stream Processing", "Apache Flink",
    # ---------------------------------------------- machine learning / data
    "Machine Learning", "Deep Learning", "Natural Language Processing",
    "Computer Vision", "Reinforcement Learning", "Supervised Learning",
    "Unsupervised Learning", "Neural Networks",
    "Convolutional Neural Networks", "Recurrent Neural Networks",
    "Transformers", "Large Language Models", "Prompt Engineering",
    "Retrieval Augmented Generation", "Model Fine-Tuning", "Vector Embeddings",
    "Semantic Search", "Feature Engineering", "Model Evaluation",
    "Model Deployment", "MLOps", "Explainable AI",
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "XGBoost", "LightGBM",
    "CatBoost", "Hugging Face Transformers", "LangChain", "LlamaIndex",
    "OpenCV", "spaCy", "NLTK", "Gensim",
    "NumPy", "pandas", "Polars", "SciPy", "Matplotlib", "Seaborn", "Plotly",
    "Jupyter Notebook", "Apache Spark", "Apache Airflow", "dbt", "Databricks",
    "Snowflake", "Apache Hadoop",
    "Data Analysis", "Data Visualization", "Data Engineering",
    "Data Warehousing", "Data Modeling", "Data Cleaning",
    "ETL", "Web Scraping", "Beautiful Soup", "Scrapy",
    "Statistics", "Probability", "Linear Algebra", "Calculus",
    "Discrete Mathematics", "Numerical Methods", "Optimization",
    "Time Series Analysis", "A/B Testing", "Hypothesis Testing",
    "Recommender Systems", "Anomaly Detection", "Clustering",
    "Dimensionality Reduction", "Information Retrieval",
    # ----------------------------------------------------------- testing
    "Unit Testing", "Integration Testing", "End-to-End Testing",
    "Test-Driven Development", "Behavior-Driven Development", "Regression Testing",
    "Load Testing", "Performance Testing", "Smoke Testing", "Code Coverage",
    "Mocking", "Test Automation", "Quality Assurance",
    "pytest", "unittest", "JUnit", "TestNG", "Mockito", "Jest", "Vitest",
    "Mocha", "Chai", "Cypress", "Playwright", "Selenium", "Puppeteer",
    "Postman", "Insomnia", "JMeter", "Locust",
    # -------------------------------------------------------- apis / web
    "REST APIs", "GraphQL", "gRPC", "WebSockets", "Server-Sent Events",
    "OpenAPI", "Swagger", "API Design", "API Versioning", "API Gateway",
    "Rate Limiting", "Caching", "CDN",
    "CORS", "HTTP", "TCP/IP", "DNS",
    "Web Performance Optimization", "Search Engine Optimization",
    "Webhooks", "Idempotency", "Pagination",
    # ---------------------------------------------------------- security
    "Authentication", "Authorization", "JWT", "OAuth 2.0",
    "OpenID Connect", "Single Sign-On", "Session Management",
    "Role-Based Access Control", "Multi-Factor Authentication",
    "Cryptography", "Encryption", "Hashing", "PKI",
    "TLS", "Application Security", "Secure Coding",
    "Penetration Testing", "Vulnerability Assessment", "Threat Modeling",
    "Network Security", "OWASP Top 10", "SAST",
    "Reverse Engineering", "Malware Analysis", "Digital Forensics",
    "Ethical Hacking", "Capture The Flag", "Incident Response",
    "Security Auditing", "Zero Trust Architecture",
    # ------------------------------------------- computer science concepts
    "Data Structures", "Algorithms", "Algorithm Analysis",
    "Computational Complexity", "Dynamic Programming", "Graph Theory",
    "Recursion", "Sorting Algorithms", "Search Algorithms",
    "Operating Systems", "Computer Networks", "Computer Architecture",
    "Compilers", "Programming Language Theory", "Automata Theory",
    "Distributed Systems", "Microservices", "Monolithic Architecture",
    "Software Architecture", "System Design", "Domain-Driven Design",
    "Hexagonal Architecture", "Design Patterns", "SOLID Principles",
    "Object-Oriented Programming", "Functional Programming",
    "Concurrent Programming", "Asynchronous Programming", "Multithreading",
    "Parallel Computing", "Memory Management", "Garbage Collection",
    "Operating System Scheduling", "Fault Tolerance", "Scalability",
    "High Availability", "Consistency Models", "CAP Theorem",
    # ------------------------------------------------- tooling / practice
    "Git", "GitHub", "GitLab", "Bitbucket", "Version Control",
    "Branching Strategies", "Code Review", "Pair Programming", "Refactoring",
    "Clean Code", "Technical Documentation", "Debugging", "Profiling",
    "Performance Tuning", "Agile Methodologies", "Scrum", "Kanban",
    "Jira", "Confluence", "Trello", "Notion", "Linear",
    "Visual Studio Code", "IntelliJ IDEA", "PyCharm", "Visual Studio",
    "Xcode", "Android Studio", "Vim", "Postman Collections",
    "Feature Flags", "Semantic Versioning", "Monorepo Management",
    # ------------------------------------------------- graphics and games
    "Unity", "Unreal Engine", "Godot", "Game Development", "Game Physics",
    "Computer Graphics", "OpenGL", "Vulkan", "DirectX", "WebGL",
    "Shader Programming", "3D Modeling", "Blender", "Physics Simulation",
    "Augmented Reality", "Virtual Reality",
    # ---------------------------------------------- embedded and hardware
    "Embedded Systems", "Internet of Things", "Arduino", "Raspberry Pi",
    "Microcontrollers", "Real-Time Operating Systems", "Firmware Development",
    "ROS", "Robotics", "Autonomous Systems",
    "Signal Processing", "Control Systems", "FPGA",
    "VHDL", "Verilog", "Sensor Fusion", "Serial Communication Protocols",
    "Computer-Aided Design",
    # --------------------------------------------------------- design/ux
    "User Interface Design", "User Experience Design", "Figma", "Adobe XD",
    "Wireframing", "Prototyping", "Design Systems", "Usability Testing",
    "Adobe Photoshop", "Adobe Illustrator",
    # -------------------------------------------------------- blockchain
    "Blockchain", "Smart Contracts", "Ethereum", "Web3.js", "Ethers.js",
    "Hardhat", "Decentralized Applications",
    # ------------------------------------------------ business / analytics
    "Microsoft Excel", "Power BI", "Tableau", "Looker", "Google Analytics",
    "Business Intelligence", "Requirements Analysis", "Technical Writing",
]
# fmt: on


def _skills_table() -> sa.Table:
    return sa.table("skills", sa.column("skill_name", sa.Text))


def upgrade() -> None:
    # ON CONFLICT DO NOTHING makes this safe to re-run and safe against rows
    # someone inserted by hand. The functional unique index on
    # lower(btrim(skill_name)) is what catches the duplicates.
    statement = pg_insert(_skills_table()).values(
        [{"skill_name": name} for name in SKILLS]
    )
    op.get_bind().execute(statement.on_conflict_do_nothing())


def downgrade() -> None:
    table = _skills_table()
    op.get_bind().execute(table.delete().where(table.c.skill_name.in_(SKILLS)))
