<?php
// Configuración de la base de datos
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "BD_DHT22_V0";

// Crear conexión
$conn = new mysqli($servername, $username, $password, $dbname);

// Verificar conexión
if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
}

// Leer el contenido JSON del cuerpo de la solicitud
$contenidoJSON = file_get_contents("php://input");

// Decodificar el JSON
$datos = json_decode($contenidoJSON, true);

// Verificar si la decodificación fue exitosa y contiene los datos esperados
if ($datos && isset($datos['disp_id']) && isset($datos['temp']) && isset($datos['humed']) &&
    isset($datos['ADCtem']) && isset($datos['ADC0']) && isset($datos['aux'])) {

    // Obtener los datos
    $disp_id = $datos['disp_id'];
    $temp    = $datos['temp'];
    $humed   = $datos['humed'];
    $ADCtem  = $datos['ADCtem'];
    $ADC0    = $datos['ADC0'];
    $aux     = $datos['aux'];

    // Preparar consulta SQL
    $sql = "INSERT INTO DatosDHT22 (disp_id, temp, humed, ADCtem, ADC0, aux)
            VALUES (?, ?, ?, ?, ?, ?)";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param("iddddd", $disp_id, $temp, $humed, $ADCtem, $ADC0, $aux);

    if ($stmt->execute()) {
        echo json_encode(["status" => "success", "message" => "Datos insertados correctamente"]);
    } else {
        echo json_encode(["status" => "error", "message" => $stmt->error]);
    }

    $stmt->close();
} else {
    echo json_encode(["status" => "error", "message" => "JSON inválido o campos incompletos"]);
}

$conn->close();
?>

