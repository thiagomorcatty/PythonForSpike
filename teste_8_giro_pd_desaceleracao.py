import motor_pair
import runloop
from hub import port, motion_sensor

async def turn_pd(target_angle, kp=2.5, kd=5.0):
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    last_error = 0
    settle_count = 0
    
    print("Teste 8: Giro com PD e Desaceleração")
    
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        error = target_angle - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        
        # Derivativo (freia se a mudança for brusca)
        derivative = error - last_error
        last_error = error
        
        velocity = (error * kp) + (derivative * kd)
        abs_v = abs(velocity)
        
        # Limites
        if abs_v > 300: velocity = 300 if velocity > 0 else -300
        if abs_v < 40: velocity = 40 if velocity > 0 else -40
        
        # Critério de parada: erro < 1 grau por 0.2s (20 ciclos de 10ms)
        if abs(error) < 1.0:
            settle_count += 1
            if settle_count > 20: break
        else:
            settle_count = 0
            
        motor_pair.move(motor_pair.PAIR_1, 100 if error > 0 else -100, velocity=int(abs(velocity)))
        await runloop.sleep_ms(10)
    
    motor_pair.stop(motor_pair.PAIR_1)
    print("Giro concluído com precisão PD.")

runloop.run(turn_pd(90))
