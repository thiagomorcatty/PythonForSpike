import motor_pair
import runloop
from hub import port, motion_sensor
import motor

# Constante calibrada
CM_TO_DEG = 20.65

async def move_straight(dist_cm, velocity):
    target_deg = dist_cm * CM_TO_DEG
    motor.reset_relative_position(port.A, 0)
    motor.reset_relative_position(port.B, 0)
    target_yaw = motion_sensor.tilt_angles()[0] * -0.1
    while True:
        pos = (abs(motor.relative_position(port.A)) + abs(motor.relative_position(port.B))) / 2
        if pos >= target_deg: break
        error = target_yaw - (motion_sensor.tilt_angles()[0] * -0.1)
        while error > 180: error -= 360
        while error < -180: error += 360
        motor_pair.move(motor_pair.PAIR_1, int(error * 1.2), velocity=velocity)
        await runloop.sleep_ms(10)
    motor_pair.stop(motor_pair.PAIR_1)

async def turn_precise(target_yaw):
    while True:
        current = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw - current
        while error > 180: error -= 360
        while error < -180: error += 360
        if abs(error) < 0.5: break
        steering = 100 if error > 0 else -100
        motor_pair.move(motor_pair.PAIR_1, steering, velocity=150)
        await runloop.sleep_ms(10)
    motor_pair.stop(motor_pair.PAIR_1)

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    print("Teste 14: Trajetória em S")
    
    print("Reta 30cm")
    await move_straight(30, 300)
    
    print("Curva 45° Direita")
    await turn_precise(45)
    
    print("Curva 45° Esquerda (para alinhar paralelo)")
    await turn_precise(0)
    
    print("Reta 30cm")
    await move_straight(30, 300)
    
    print("S concluído. Robô deve estar paralelo à posição inicial.")

runloop.run(main())
