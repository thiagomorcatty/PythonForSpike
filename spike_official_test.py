from hub import light_matrix, port
import runloop
import motor
import force_sensor
import device

async def main():
    print("--- Teste de Hardware Profundo ---")
    
    # 1. Verificar o que o Hub ve em cada porta
    ports = [port.A, port.B, port.C, port.D]
    for p in ports:
        try:
            dev_id = device.get_device_id(p)
            print("Porta {}: ID do Dispositivo = {}".format(p, dev_id))
        except:
            print("Porta {}: Erro ao ler ID".format(p))

    # 2. Testar Motores com PWM (Energia Direta)
    motor_ports = [port.A, port.B, port.D]
    for p in motor_ports:
        try:
            print("Enviando PWM 100 para porta {}...".format(p))
            # motor.pwm envia energia direta (0 a 100)
            motor.pwm(p, 100)
            await runloop.sleep_ms(2000)
            motor.stop(p)
            print("Porta {} testada.".format(p))
        except Exception as e:
            print("Erro motor porta {}: {}".format(p, e))

    # 3. Testar Sensor de Toque
    print("\n--- Testando Sensor C ---")
    try:
        for _ in range(50):
            # Tenta ler o valor bruto do sensor
            if force_sensor.is_pressed(port.C):
                print("TOQUE DETECTADO!")
                await light_matrix.write("YES")
                break
            await runloop.sleep_ms(100)
    except Exception as e:
        print("Erro sensor: {}".format(e))

    print("Fim do teste.")

runloop.run(main())
