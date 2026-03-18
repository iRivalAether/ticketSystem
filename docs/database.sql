-- ============================================
-- Sistema de Gestión de Tickets
-- Script de Creación de Base de Datos MySQL
-- ============================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS ticket_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Usar la base de datos
USE ticket_system;

-- Crear usuario (opcional)
-- CREATE USER 'ticketuser'@'localhost' IDENTIFIED BY 'password123';
-- GRANT ALL PRIVILEGES ON ticket_system.* TO 'ticketuser'@'localhost';
-- FLUSH PRIVILEGES;

-- ============================================
-- NOTA IMPORTANTE:
-- Las tablas serán creadas automáticamente
-- por Django mediante migraciones.
-- 
-- Para crear las tablas, ejecutar:
-- python manage.py makemigrations
-- python manage.py migrate
-- ============================================

-- Verificar que la base de datos fue creada correctamente
SELECT 
    SCHEMA_NAME as 'Base de Datos',
    DEFAULT_CHARACTER_SET_NAME as 'Charset',
    DEFAULT_COLLATION_NAME as 'Collation'
FROM information_schema.SCHEMATA 
WHERE SCHEMA_NAME = 'ticket_system';
