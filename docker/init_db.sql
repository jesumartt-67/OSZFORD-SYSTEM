-- Creación de la base de datos
CREATE DATABASE IF NOT EXISTS oszford_db;
USE oszford_db;

-- 1. Tabla de Colaboradores (Incluye MFA y Seguridad)
CREATE TABLE IF NOT EXISTS colaboradores (
    id_colaborador INT AUTO_INCREMENT PRIMARY KEY, -- ID técnico (para la DB)
    cedula VARCHAR(15) UNIQUE NOT NULL,            -- ID Real (para el negocio)
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    mfa_secret VARCHAR(32), 
    cargo VARCHAR(50),
    licencia_nro VARCHAR(20),
    licencia_vigencia DATE,
    activo BOOLEAN DEFAULT TRUE
);

-- 2. Tabla de Vehículos
CREATE TABLE IF NOT EXISTS vehiculos (
    placa VARCHAR(10) PRIMARY KEY,
    tipo ENUM('Moto', 'Bicicleta', 'Patineta Eléctrica', 'Moto Eléctrica') NOT NULL,
    propiedad ENUM('Empresa', 'Propio') NOT NULL,
    soat_vencimiento DATE,
    tecnico_vencimiento DATE,
    foto_referencia_url VARCHAR(255) -- Link a Cloud Storage
);

-- 3. Tabla de Transferencias / Relevo (QR Dinámico)
CREATE TABLE IF NOT EXISTS transferencias_relevo (
    id_transferencia INT AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(10),
    id_colaborador_sale INT,
    id_colaborador_entra INT NULL, -- Se llena cuando el otro escanea
    km_entrega DECIMAL(10,2),
    token_qr_hash VARCHAR(64) UNIQUE, -- El token firmado que va en el QR
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmada BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (placa) REFERENCES vehiculos(placa),
    FOREIGN KEY (id_colaborador_sale) REFERENCES colaboradores(id_colaborador),
    FOREIGN KEY (id_colaborador_entra) REFERENCES colaboradores(id_colaborador)
);

-- 4. Tabla de Inspecciones Preoperacionales
CREATE TABLE IF NOT EXISTS inspecciones (
    id_inspeccion INT AUTO_INCREMENT PRIMARY KEY,
    id_colaborador INT,
    placa VARCHAR(10),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    km_registro DECIMAL(10,2),
    estado_visual_ia ENUM('Verde', 'Amarillo', 'Rojo'),
    confianza_ia FLOAT NULL,	
    url_foto_verificacion VARCHAR(255),
    alerta_enviada BOOLEAN DEFAULT TRUE NULL,
    novedades TEXT,
    FOREIGN KEY (id_colaborador) REFERENCES colaboradores(id_colaborador),
    FOREIGN KEY (placa) REFERENCES vehiculos(placa)
);