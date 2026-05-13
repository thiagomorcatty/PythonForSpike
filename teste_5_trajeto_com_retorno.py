import motor_pair
import runloop
from hub import port, motion_sensor
import utime
import motor

async def move_straight_with_gyro(pair, left_port, right_port, target_degrees, velocity):
    """
    Move o robô em linha reta usando o giroscópio para corrigir o rumo,
    com rampa de desaceleração para precisão total.
    """
    motor.reset_relative_position(left_port, 0)
    motor.reset_relative_position(right_port, 0)
    
    target_yaw = motion_sensor.tilt_angles()[0] * -0.1
    kp = 1.2 
    
    print("Movimento Preciso: {} graus | Rumo: {:.1f}°".format(target_degrees, target_yaw))
    
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        pos_left = motor.relative_position(left_port)
        pos_right = motor.relative_position(right_port)
        current_distance = (abs(pos_left) + abs(pos_right)) / 2
        
        remaining = abs(target_degrees) - current_distance
        
        if remaining <= 0:
            break
            
        # Rampa de Desaceleração: Reduz a velocidade nos últimos 400 graus
        if remaining < 400:
            # Calcula velocidade proporcional ao que falta, mínimo de 100
            v_scaled = int(velocity * (remaining / 400))
            if abs(v_scaled) < 100:
                v_scaled = 100 if velocity > 0 else -100
            current_vel = v_scaled
        else:
            current_vel = velocity

        # Correção do Giro
        error = target_yaw - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        
        correction = error * kp
        if velocity < 0:
            correction = -correction

        if correction > 25: correction = 25
        if correction < -25: correction = -25
        
        motor_pair.move(pair, int(correction), velocity=current_vel)
        await runloop.sleep_ms(10)
    
    motor_pair.stop(pair)

async def turn_to_angle(pair, target_yaw_deg, velocity):
    """
    Gira o robô até um ângulo absoluto.
    """
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw_deg - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        
        if abs(error) < 1.0:
            break
            
        steering = 100 if error > 0 else -100
        current_vel = velocity if abs(error) > 15 else 60
        
        motor_pair.move(pair, steering, velocity=current_vel)
        await runloop.sleep_ms(10)
        
    motor_pair.stop(pair)

async def main():
    print("--- Teste 5 Corrigido: Retorno por Encoders ---")
    
    p_left = port.A
    p_right = port.B
    
    # Setup
    print("Alinhando e Calibrando...")
    await motor.run_to_absolute_position(p_left, 0, 300)
    await motor.run_to_absolute_position(p_right, 0, 300)
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(2000)
    
    motor_pair.pair(motor_pair.PAIR_1, p_left, p_right)
    
    # Definimos as distâncias em GRAUS de rotação do motor
    distancia_1 = 1500 # Aprox. 3 segundos a 350 vel
    distancia_2 = 1000 # Aprox. 2 segundos a 350 vel
    
    vel_ida = 350
    vel_volta = 1000 # Velocidade máxima pedida
    vel_giro = 150
    
    # 1. IDA
    print("\n--- FASE 1: IDA (Vel: {}) ---".format(vel_ida))
    await move_straight_with_gyro(motor_pair.PAIR_1, p_left, p_right, distancia_1, vel_ida)
    await runloop.sleep_ms(500)
    
    await turn_to_angle(motor_pair.PAIR_1, 60, vel_giro)
    await runloop.sleep_ms(500)
    
    await move_straight_with_gyro(motor_pair.PAIR_1, p_left, p_right, distancia_2, vel_ida)
    
    print("Pausa no destino...")
    await runloop.sleep_ms(2000)
    
    # 2. VOLTA
    print("\n--- FASE 2: VOLTA (Vel: {}) ---".format(vel_volta))
    # Volta a mesma distância exata (distancia_2) mas com velocidade negativa
    await move_straight_with_gyro(motor_pair.PAIR_1, p_left, p_right, distancia_2, -vel_volta)
    await runloop.sleep_ms(500)
    
    await turn_to_angle(motor_pair.PAIR_1, 0, vel_giro)
    await runloop.sleep_ms(500)
    
    # Volta a mesma distância exata (distancia_1)
    await move_straight_with_gyro(motor_pair.PAIR_1, p_left, p_right, distancia_1, -vel_volta)

    print("\nRetorno concluído!")
    print("Erro de orientação final: {:.2f}°".format(motion_sensor.tilt_angles()[0] * -0.1))

runloop.run(main())
