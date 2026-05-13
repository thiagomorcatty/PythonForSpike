import motor_pair
import runloop
from hub import port, motion_sensor

async def move_arc(radius_cm, target_angle_absolute, velocity):
    # Steering fixo para simular o raio
    steering = int(500 / radius_cm)
    while True:
        current = motion_sensor.tilt_angles()[0] * -0.1
        error = target_angle_absolute - current
        while error > 180: error -= 360
        while error < -180: error += 360
        
        if abs(error) < 5.0: break # Margem maior para arco
            
        # Determina direção do steering baseado no alvo
        final_steering = steering if error > 0 else -steering
        motor_pair.move(motor_pair.PAIR_1, final_steering, velocity=velocity)
        await runloop.sleep_ms(10)
    motor_pair.stop(motor_pair.PAIR_1)

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    print("Teste 15: Figura em Oito")
    
    # Reseta gyro para começar do zero
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(1000)
    
    print("Círculo para Direita (0 a 180)")
    await move_arc(25, 175, 300) # Gira 180 graus
    
    print("Círculo para Esquerda (180 a 0)")
    await move_arc(25, 0, 300) # Volta para 0
    
    print("Oito concluído.")

runloop.run(main())
