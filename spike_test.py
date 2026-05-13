from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Port, Stop, Color, Button
from pybricks.tools import wait

# Inicializa o Hub
hub = PrimeHub()

def test_hub():
    print("--- Testando Hub ---")
    hub.display.text("OK")
    hub.light.on(Color.GREEN)
    wait(1000)
    print("Bateria:", hub.battery.voltage(), "mV")

def test_motors():
    print("\n--- Testando Motores (Portas A e B) ---")
    try:
        motor_a = Motor(Port.A)
        motor_b = Motor(Port.B)
        
        print("Girando Motor A...")
        motor_a.run_target(500, 90) # Velocidade 500, angulo 90
        
        print("Girando Motor B...")
        motor_b.run_target(500, -90)
        
        wait(500)
        motor_a.stop()
        motor_b.stop()
        print("Motores OK!")
    except Exception as e:
        print("Erro nos motores: Verifique se estão nas portas A e B.")

def test_sensors():
    print("\n--- Testando Sensores (C: Cor, D: Distância) ---")
    try:
        # Tenta inicializar o sensor de cor na porta C
        color_sensor = ColorSensor(Port.C)
        print("Cor detectada na Porta C:", color_sensor.color())
    except:
        print("Sensor de Cor não detectado na Porta C.")

    try:
        # Tenta inicializar o sensor de distância na porta D
        dist_sensor = UltrasonicSensor(Port.D)
        print("Distância detectada na Porta D:", dist_sensor.distance(), "mm")
    except:
        print("Sensor de Distância não detectado na Porta D.")

# Execução dos testes
print("Iniciando testes do Spike Prime...")
test_hub()
test_motors()
test_sensors()

print("\nTestes concluídos! Pressione o botão central para encerrar.")
while not any(hub.buttons.pressed()):
    wait(10)
hub.system.shutdown()
