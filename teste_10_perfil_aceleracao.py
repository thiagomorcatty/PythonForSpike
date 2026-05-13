import motor_pair
import runloop
from hub import port, motion_sensor
import motor

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    distancia_cm = 100 # Teste longo de 1 metro
    target_deg = distancia_cm * 20.65
    
    accel_pct = 0.2
    decel_pct = 0.3
    max_vel = 600
    min_vel = 80
    
    print("Teste 10: Perfil Aceleração/Frenagem")
    
    motor.reset_relative_position(port.A, 0)
    motor.reset_relative_position(port.B, 0)
    target_yaw = motion_sensor.tilt_angles()[0] * -0.1

    while True:
        pos = (abs(motor.relative_position(port.A)) + abs(motor.relative_position(port.B))) / 2
        pct = pos / target_deg
        if pct >= 1.0: break
            
        # Cálculo da velocidade
        if pct < accel_pct:
            # Aceleração linear
            v = min_vel + (max_vel - min_vel) * (pct / accel_pct)
        elif pct > (1 - decel_pct):
            # Frenagem linear
            v = min_vel + (max_vel - min_vel) * ((1 - pct) / decel_pct)
        else:
            # Velocidade de cruzeiro
            v = max_vel
            
        # Correção gyro básica (Kp=1.0)
        error = target_yaw - (motion_sensor.tilt_angles()[0] * -0.1)
        while error > 180: error -= 360
        while error < -180: error += 360
        
        motor_pair.move(motor_pair.PAIR_1, int(error * 1.0), velocity=int(v))
        await runloop.sleep_ms(10)
        
    motor_pair.stop(motor_pair.PAIR_1)
    print("Movimento perfilado concluído.")

runloop.run(main())
