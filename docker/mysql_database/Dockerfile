# ---------------------------------------------------------------------------------------------------------------------
# ** stage 1: production image
# ---------------------------------------------------------------------------------------------------------------------

# ** info: declaration of the image base version
FROM mysql:8.0.36

# ** info: declaration of the container env variables
ENV MYSQL_ROOT_PASSWORD=credit_system_password
ENV MYSQL_PASSWORD=credit_system_password
ENV MYSQL_DATABASE=credit_system_db
ENV MYSQL_USER=credit_system_user

# ** info: copying the migrations from the building context to the initdb folder
COPY migrations/mysql_database /docker-entrypoint-initdb.d/
