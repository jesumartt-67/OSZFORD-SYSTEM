USE oszford_db;

-- Limpiar datos previos para evitar errores de duplicidad en la Hackatón
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE transferencias_relevo;
TRUNCATE TABLE inspecciones;
TRUNCATE TABLE vehiculos;
TRUNCATE TABLE colaboradores;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Insertar en 'colaboradores' (Ajustado a tus nombres de columna)
INSERT INTO colaboradores (id_colaborador, cedula, nombre, email, password_hash, mfa_secret, cargo, licencia_nro, licencia_vigencia, activo) 
VALUES 
(101, '111222333', 'Jesús Fernando', 'jesumartt@gmail.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s5Arg6ijBxAG.', 'JBSWY3DPEHPK3PXP', 'Analista de Operaciones', '70123456-A', '2028-12-31', 1),
(102, '444555666', 'Maria Restrepo', 'm.restrepo@ponao.edu.co', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s5Arg6ijBxAG.', 'KREWY3DPEHPK3PXP', 'Supervisora de Zona', '80987654-B', '2026-05-15', 1),
(103, '777888999', 'Carlos Angulo', 'c.angulo@ponao.edu.co', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s5Arg6ijBxAG.', 'ASWEY3DPEHPK3PXP', 'Escolta Motorizado', '90554433-C', '2027-08-20', 1);

-- 2. Insertar en 'vehiculos' (Ajustado a tus ENUMS de tipo y propiedad)
INSERT INTO vehiculos (placa, tipo, propiedad, soat_vencimiento, tecnico_vencimiento, foto_referencia_url)
VALUES 
('GHT-45C', 'Moto', 'Propio', '2025-12-31', '2025-10-15', 'https://storage.google.com/oszford/moto1.jpg'),
('BJC-123', 'Bicicleta', 'Empresa', NULL, NULL, 'https://storage.google.com/oszford/bici1.jpg'),
('XYZ-89E', 'Moto Eléctrica', 'Propio', '2026-01-20', '2025-11-30', 'https://storage.google.com/oszford/motoelec1.jpg');

-- 3. Insertar en 'inspecciones' (Ajustado a tus nombres de columna)
INSERT INTO inspecciones (id_colaborador, placa, km_registro, estado_visual_ia, url_foto_verificacion, novedades)
VALUES 
(101, 'GHT-45C', 12500.50, 'Verde', 'https://storage.google.com/oszford/inspec1.jpg', 'Sin novedades'),
(102, 'BJC-123', 450.00, 'Amarillo', 'https://storage.google.com/oszford/inspec2.jpg', 'Cadena un poco suelta');

-- 4. Insertar en 'transferencias_relevo'
INSERT INTO transferencias_relevo (placa, id_colaborador_sale, id_colaborador_entra, km_entrega, token_qr_hash, confirmada)
VALUES 
('GHT-45C', 101, 103, 12510.00, 'hash_generado_123456', 1);