import motor_pair
import runloop
from hub import port, motion_sensor
import utime
import motor

# Constante de conversão: graus de motor por cm (roda padrão Spike = 5.6cm diâmetro)
# Circunferência = 17.6cm -> 360 / 17.6 = ~20.45
CM_TO_DEG = 20.45

async def move_straight_with_gyro(pair, left_port, right_port, distance_cm, velocity):
    """
    Move o robô em linha reta por uma distância em CM usando correção de giro.
    """
    target_degrees = distance_cm * CM_TO_DEG
    motor.reset_relative_position(left_port, 0)
    motor.reset_relative_position(right_port, 0)
    
    target_yaw = motion_sensor.tilt_angles()[0] * -0.1
    kp = 1.2 
    
    print("Retângulo: {}cm ({:.0f}°) | Rumo: {:.1f}°".format(distance_cm, target_degrees, target_yaw))
    
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

        error = target_yaw - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        
        correction = error * kp
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

async def run_attachment(port_f):
    """
    Movimenta o anexo na porta F: 180 graus para um lado, 180 para o outro.
    """
    print("Ativando anexo na Porta F (180°)...")
    try:
        # Move 180 graus sentido horário
        await motor.run_for_degrees(port_f, 180, 500)
        # Move 180 graus sentido anti-horário
        await motor.run_for_degrees(port_f, -180, 500)
        print("Anexo concluído.")
    except Exception as e:
        print("Erro no anexo F: {}".format(e))

async def main():
    print("--- Teste 6: Retângulo com Anexo ---")
    
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
    
    vel_reta = 400
    vel_giro = 150
    
    # Trajeto do Retângulo: 25cm -> 50cm -> 25cm -> 50cm
    lados = [25, 50, 25, 50]
    
    for i, distancia in enumerate(lados):
        lado_num = i + 1
        alvo_yaw = (i * 90) % 360
        if alvo_yaw > 180: alvo_yaw -= 360
        
        print("\n--- Lado {} ({}cm) ---".format(lado_num, distancia))
        
        # Se for o lado de 50cm, iniciamos o anexo em paralelo
        if distancia == 50:
            # No SPIKE 3, para rodar em paralelo sem bloquear a reta:
            runloop.spawn(run_attachment(p_anexo))
        
        # Move em linha reta com correção de giro
        await move_straight_with_gyro(motor_pair.PAIR_1, p_left, p_right, distancia, vel_reta)
        
        await runloop.sleep_ms(500)
        
        # Curva para o próximo lado (exceto após o último lado, se quiser parar na orientação inicial)
        proximo_alvo = ((i + 1) * 90) % 360
        if proximo_alvo > 180: proximo_alvo -= 360
        
        await turn_to_angle(motor_pair.PAIR_1, proximo_alvo, vel_giro)
        await runloop.sleep_ms(500)

    print("\nRetângulo com anexo concluído!")

runloop.run(main())
