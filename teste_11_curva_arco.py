import motor_pair
import runloop
from hub import port, motion_sensor

async def move_arc(radius_cm, target_angle_relative, velocity):
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    print("Teste 11: Curva em Arco")
    
    start_yaw = motion_sensor.tilt_angles()[0] * -0.1
    target_yaw = start_yaw + target_angle_relative
    
    # Steering proporcional ao inverso do raio
    # Valor 500 é uma estimativa para a largura entre rodas do Spike
    steering = int(500 / radius_cm)
    if target_angle_relative < 0:
        steering = -steering
        
    while True:
        current = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw - current
        while error > 180: error -= 360
        while error < -180: error += 360
        
        if abs(error) < 2.0: break
            
        motor_pair.move(motor_pair.PAIR_1, steering, velocity=velocity)
        await runloop.sleep_ms(10)
        
    motor_pair.stop(motor_pair.PAIR_1)
    print("Arco concluído.")

# Exemplo: Arco de raio 25cm para 90 graus
runloop.run(move_arc(25, 90, 300))
