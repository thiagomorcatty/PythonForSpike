import motor_pair
import runloop
from hub import port, motion_sensor

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    print("Teste 9: Curva Progressiva")
    
    # Início 0°, Alvo Final 90°
    # Vai mudando o alvo gradualmente enquanto gira
    for alvo in range(0, 91, 5): # Incrementos de 5 graus
        while True:
            current = motion_sensor.tilt_angles()[0] * -0.1
            error = alvo - current
            while error > 180: error -= 360
            while error < -180: error += 360
            
            if abs(error) < 1.0: break
                
            steering = 100 if error > 0 else -100
            motor_pair.move(motor_pair.PAIR_1, steering, velocity=100)
            await runloop.sleep_ms(10)
        print("Atingiu alvo parcial: {}°".format(alvo))
        
    motor_pair.stop(motor_pair.PAIR_1)
    print("Curva progressiva finalizada.")

runloop.run(main())
