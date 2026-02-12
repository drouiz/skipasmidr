# SuiteCRM 8 Docker Image
FROM php:8.2-apache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    libldap2-dev \
    libc-client2007e-dev \
    libkrb5-dev \
    libicu-dev \
    zip \
    unzip \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions required by SuiteCRM
RUN docker-php-ext-configure imap --with-kerberos --with-imap-ssl \
    && docker-php-ext-install \
    pdo_mysql \
    mysqli \
    mbstring \
    exif \
    pcntl \
    bcmath \
    gd \
    zip \
    ldap \
    imap \
    intl \
    soap \
    opcache

# Enable Apache modules
RUN a2enmod rewrite headers expires

# Configure PHP
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini" \
    && sed -i 's/memory_limit = .*/memory_limit = 512M/' "$PHP_INI_DIR/php.ini" \
    && sed -i 's/upload_max_filesize = .*/upload_max_filesize = 64M/' "$PHP_INI_DIR/php.ini" \
    && sed -i 's/post_max_size = .*/post_max_size = 64M/' "$PHP_INI_DIR/php.ini" \
    && sed -i 's/max_execution_time = .*/max_execution_time = 300/' "$PHP_INI_DIR/php.ini" \
    && sed -i 's/max_input_time = .*/max_input_time = 300/' "$PHP_INI_DIR/php.ini"

# Set working directory
WORKDIR /var/www/html

# Download and extract SuiteCRM 8 from GitHub releases
ARG SUITECRM_VERSION=8.7.1
RUN curl -L -o suitecrm.zip "https://github.com/salesagility/SuiteCRM-Core/releases/download/v${SUITECRM_VERSION}/SuiteCRM-${SUITECRM_VERSION}.zip" \
    && unzip suitecrm.zip -d /tmp/suitecrm \
    && rm suitecrm.zip \
    && cp -r /tmp/suitecrm/*/* . 2>/dev/null || cp -r /tmp/suitecrm/* . \
    && rm -rf /tmp/suitecrm \
    && chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html \
    && find /var/www/html -type d -exec chmod 775 {} \; \
    && chmod -R 775 /var/www/html/public/legacy/cache 2>/dev/null || true \
    && chmod -R 775 /var/www/html/public/legacy/custom 2>/dev/null || true \
    && chmod -R 775 /var/www/html/public/legacy/modules 2>/dev/null || true \
    && chmod -R 775 /var/www/html/public/legacy/upload 2>/dev/null || true

# Apache configuration
RUN echo '<VirtualHost *:80>\n\
    DocumentRoot /var/www/html/public\n\
    <Directory /var/www/html/public>\n\
        AllowOverride All\n\
        Require all granted\n\
    </Directory>\n\
    ErrorLog ${APACHE_LOG_DIR}/error.log\n\
    CustomLog ${APACHE_LOG_DIR}/access.log combined\n\
</VirtualHost>' > /etc/apache2/sites-available/000-default.conf

# Cron for SuiteCRM scheduler
RUN echo "* * * * * cd /var/www/html && php bin/console suitecrm:app:process-async-actions >> /var/log/cron.log 2>&1" > /etc/cron.d/suitecrm \
    && chmod 0644 /etc/cron.d/suitecrm \
    && crontab /etc/cron.d/suitecrm

EXPOSE 80

CMD ["apache2-foreground"]
