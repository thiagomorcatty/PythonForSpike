import motor_pair
import runloop
from hub import port, motion_sensor
import utime
import motor

# Constante de conversão: graus de motor por cm (roda padrão Spike = 5.6cm diâmetro)
# Circunferência = 17.6cm -> 360 / 17.6 = ~20.45
# Constante de conversão ajustada para compensar o erro de 2cm (Calibração: 20.65)
CM_TO_DEG = 20.65

async def move_straight_with_gyro(pair, left_port, right_port, distance_cm, velocity, anexo_port=None):
    """
    Move o robô em linha reta com correção de giro e controle de anexo integrado.
    """
    target_degrees = distance_cm * CM_TO_DEG
    motor.reset_relative_position(left_port, 0)
    motor.reset_relative_position(right_port, 0)
    
    start_time = utime.ticks_ms()
    target_yaw = motion_sensor.tilt_angles()[0] * -0.1
    kp = 1.2 
    
    print("Iniciando reta: {}cm | Rumo: {:.1f}°".format(distance_cm, target_yaw))
    
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        pos_left = motor.relative_position(left_port)
        pos_right = motor.relative_position(right_port)
        current_distance = (abs(pos_left) + abs(pos_right)) / 2
        
        remaining = abs(target_degrees) - current_distance
        if remaining <= 0:
            break
            
        # Rampa de desaceleração aumentada para 500 graus para maior precisão
        if remaining < 500:
            v_scaled = int(velocity * (remaining / 500))
            current_vel = v_scaled if abs(v_scaled) > 80 else (80 if velocity > 0 else -80)
        else:
            current_vel = velocity

        # Correção do Giro
        error = target_yaw - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        
        correction = error * kp
        if correction > 25: correction = 25
        if correction < -25: correction = -25
        
        motor_pair.move(pair, int(correction), velocity=current_vel)
        
        # Controle INTEGRADO do anexo (Porta F)
        if anexo_port is not None:
            tempo_decorrido = utime.ticks_diff(utime.ticks_ms(), start_time)
            if tempo_decorrido < 1000:
                motor.run(anexo_port, 300)
            elif tempo_decorrido < 2000:
                motor.run(anexo_port, -300)
            else:
                motor.stop(anexo_port)
        
        await runloop.sleep_ms(10)
    
    motor_pair.stop(pair)
    if anexo_port is not None:
        motor.stop(anexo_port)

async def turn_to_angle(pair, target_yaw_deg, velocity):
    """
    Gira o robô até um ângulo absoluto.
    """
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw_deg - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        
        if abs(error) < 0.5: # Precisão de curva aumentada para 0.5 graus
            break
            
        steering = 100 if error > 0 else -100
        current_vel = velocity if abs(error) > 15 else 50
        
        motor_pair.move(pair, steering, velocity=current_vel)
        await runloop.sleep_ms(10)
        
    motor_pair.stop(pair)

async def main():
    print("--- Teste 6 Calibrado: Retângulo 35x70 ---")
    
    p_left = port.A
    p_right = port.B
    p_anexo = port.F
    
    # Setup inicial
    print("Preparando sistemas...")
    await motor.run_to_absolute_position(p_left, 0, 300)
    await motor.run_to_absolute_position(p_right, 0, 300)
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(2000)
    
    motor_pair.pair(motor_pair.PAIR_1, p_left, p_right)
    
    vel_reta = 350
    vel_giro = 100 # Reduzimos a velocidade de giro para 100 para evitar inércia
    
    # Trajeto: 35cm -> 70cm (com anexo) -> 35cm -> 70cm (com anexo)
    lados = [35, 70, 35, 70]
    
    for i, distancia in enumerate(lados):
        lado_num = i + 1
        alvo_yaw = (i * 90) % 360
        if alvo_yaw > 180: alvo_yaw -= 360
        
        print("\n--- Lado {} ({}cm) ---".format(lado_num, distancia))
        
        # Define se o anexo deve rodar neste lado (nos lados de 70cm)
        p_anexo_param = p_anexo if distancia == 70 else None
        
        # Executa o movimento
        await move_straight_with_gyro(motor_pair.PAIR_1, p_left, p_right, distancia, vel_reta, anexo_port=p_anexo_param)
        
        await runloop.sleep_ms(500)
        
        # Curva
        proximo_alvo = ((i + 1) * 90) % 360
        if proximo_alvo > 180: proximo_alvo -= 360
        
        await turn_to_angle(motor_pair.PAIR_1, proximo_alvo, vel_giro)
        await runloop.sleep_ms(500)

    print("\nRetângulo Calibrado Concluído!")

runloop.run(main())
