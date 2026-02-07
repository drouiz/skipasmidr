-- Auto-create databases for services that need MariaDB
-- This script runs on first MariaDB initialization

-- Dolibarr database
CREATE DATABASE IF NOT EXISTS dolibarr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON dolibarr.* TO 'admin'@'%';

-- Mautic database (if needed later)
CREATE DATABASE IF NOT EXISTS mautic CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON mautic.* TO 'admin'@'%';

-- SuiteCRM database (if needed later)
CREATE DATABASE IF NOT EXISTS suitecrm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON suitecrm.* TO 'admin'@'%';

-- Matomo database (if needed later)
CREATE DATABASE IF NOT EXISTS matomo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON matomo.* TO 'admin'@'%';

-- WordPress database (if needed later)
CREATE DATABASE IF NOT EXISTS wordpress CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON wordpress.* TO 'admin'@'%';

FLUSH PRIVILEGES;
