import motor_pair
import runloop
from hub import port, motion_sensor
import utime
import motor

# Constante de conversão: graus de motor por cm (roda padrão Spike = 5.6cm diâmetro)
# Circunferência = 17.6cm -> 360 / 17.6 = ~20.45
CM_TO_DEG = 20.45

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
            
        # Rampa de desaceleração
        if remaining < 300:
            v_scaled = int(velocity * (remaining / 300))
            current_vel = v_scaled if abs(v_scaled) > 100 else (100 if velocity > 0 else -100)
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
        
        # Controle INTEGRADO do anexo (Porta F) para evitar travar o Hub
        if anexo_port is not None:
            tempo_decorrido = utime.ticks_diff(utime.ticks_ms(), start_time)
            if tempo_decorrido < 1000:
                motor.run(anexo_port, 300) # Gira a 300 deg/s
            elif tempo_decorrido < 2000:
                motor.run(anexo_port, -300) # Gira a -300 deg/s
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
        
        if abs(error) < 1.0:
            break
            
        steering = 100 if error > 0 else -100
        current_vel = velocity if abs(error) > 15 else 60
        
        motor_pair.move(pair, steering, velocity=current_vel)
        await runloop.sleep_ms(10)
        
    motor_pair.stop(pair)

async def main():
    print("--- Teste 6 Corrigido: Retângulo com Anexo ---")
    
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
    vel_giro = 150
    
    # Trajeto: 25cm -> 50cm (com anexo) -> 25cm -> 50cm (com anexo)
    lados = [25, 50, 25, 50]
    
    for i, distancia in enumerate(lados):
        lado_num = i + 1
        alvo_yaw = (i * 90) % 360
        if alvo_yaw > 180: alvo_yaw -= 360
        
        print("\n--- Lado {} ({}cm) ---".format(lado_num, distancia))
        
        # Define se o anexo deve rodar neste lado
        p_anexo_param = p_anexo if distancia == 50 else None
        
        # Executa o movimento (o anexo agora é controlado dentro da função move_straight)
        await move_straight_with_gyro(motor_pair.PAIR_1, p_left, p_right, distancia, vel_reta, anexo_port=p_anexo_param)
        
        await runloop.sleep_ms(500)
        
        # Curva
        proximo_alvo = ((i + 1) * 90) % 360
        if proximo_alvo > 180: proximo_alvo -= 360
        
        await turn_to_angle(motor_pair.PAIR_1, proximo_alvo, vel_giro)
        await runloop.sleep_ms(500)

    print("\nRetângulo concluído!")

runloop.run(main())
