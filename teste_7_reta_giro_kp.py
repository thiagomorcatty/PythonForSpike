import motor_pair
import runloop
from hub import port, motion_sensor
import motor

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    target_yaw = motion_sensor.tilt_angles()[0] * -0.1
    kp = 1.2
    distancia_cm = 50
    target_deg = distancia_cm * 20.65
    
    print("Teste 7: Reta com Kp")
    
    while True:
        pos = (abs(motor.relative_position(port.A)) + abs(motor.relative_position(port.B))) / 2
        if pos >= target_deg: break
            
        error = target_yaw - (motion_sensor.tilt_angles()[0] * -0.1)
        while error > 180: error -= 360
        while error < -180: error += 360
        
        correction = error * kp
        motor_pair.move(motor_pair.PAIR_1, int(correction), velocity=300)
        await runloop.sleep_ms(10)
    
    motor_pair.stop(motor_pair.PAIR_1)

runloop.run(main())
