<?php
// Configuración de la conexión
$servername = "localhost";
$username = "root";
$password = "";
$database = "parcial2";
$port = 3306;

// Crear conexión
$conn = new mysqli($servername, $username, $password, $database, $port);

// Verificar conexión
if ($conn->connect_error) {
    die(json_encode(["status" => "error", "message" => "Error de conexión: " . $conn->connect_error]));
}

// Leer datos JSON del ESP32
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    echo json_encode(["status" => "error", "message" => "Datos JSON inválidos o vacíos."]);
    exit;
}

// Extraer los datos
$temperatura = isset($data['temperatura']) ? floatval($data['temperatura']) : null;
$humedad = isset($data['humedad']) ? floatval($data['humedad']) : null;
$distancia = isset($data['distancia']) ? floatval($data['distancia']) : null;
$color_led = isset($data['color_led']) ? intval($data['color_led']) : 0; // Puedes poner 0 si no mandas el color
$id_planta = isset($data['id_planta']) ? intval($data['id_planta']) : 1; // Opcional: poner 1 si no mandas id_planta

// Validaciones básicas
if ($temperatura === null || $humedad === null || $distancia === null) {
    echo json_encode(["status" => "error", "message" => "Faltan parámetros."]);
    exit;
}

// Insertar datos
$stmt = $conn->prepare("INSERT INTO sensores (temperatura, humedad, distancia, color_led, id_planta) VALUES (?, ?, ?, ?, ?)");
if ($stmt === false) {
    echo json_encode(["status" => "error", "message" => "Error en preparación de consulta: " . $conn->error]);
    exit;
}

$stmt->bind_param("dddii", $temperatura, $humedad, $distancia, $color_led, $id_planta);

if ($stmt->execute()) {
    echo json_encode(["status" => "success", "message" => "Datos insertados correctamente."]);
} else {
    echo json_encode(["status" => "error", "message" => "Error al insertar datos: " . $stmt->error]);
}

$stmt->close();
$conn->close();
?>