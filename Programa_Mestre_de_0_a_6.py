import motor_pair
import runloop
from hub import port, motion_sensor, light_matrix, button
import utime
import motor

# --- CONFIGURAÇÕES GLOBAIS ---
CM_TO_DEG = 20.65 # Calibrado no Teste 6
PORT_LEFT = port.A
PORT_RIGHT = port.B
PORT_ATTACH = port.F

# --- BIBLIOTECA DE MOVIMENTAÇÃO (O "CÉREBRO" DO ROBÔ) ---

async def move_straight(distance_cm, velocity, anexo_port=None):
    """Movimento de alta precisão com Giroscópio e Encoders."""
    target_degrees = distance_cm * CM_TO_DEG
    motor.reset_relative_position(PORT_LEFT, 0)
    motor.reset_relative_position(PORT_RIGHT, 0)
    
    start_time = utime.ticks_ms()
    target_yaw = motion_sensor.tilt_angles()[0] * -0.1
    kp = 1.2
    
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        pos_left = motor.relative_position(PORT_LEFT)
        pos_right = motor.relative_position(PORT_RIGHT)
        current_distance = (abs(pos_left) + abs(pos_right)) / 2
        
        remaining = abs(target_degrees) - current_distance
        if remaining <= 0: break
            
        # Rampa de desaceleração (frenagem suave)
        current_vel = velocity
        if remaining < 500:
            v_scaled = int(velocity * (remaining / 500))
            current_vel = v_scaled if abs(v_scaled) > 80 else (80 if velocity > 0 else -80)

        # Correção de rumo
        error = target_yaw - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        correction = error * kp
        
        # Ajuste de steering para frente/trás
        if velocity < 0: correction = -correction
        
        motor_pair.move(motor_pair.PAIR_1, int(correction), velocity=current_vel)
        
        # Controle de anexo integrado (se solicitado)
        if anexo_port:
            tempo = utime.ticks_diff(utime.ticks_ms(), start_time)
            if tempo < 1000: motor.run(anexo_port, 350)
            elif tempo < 2000: motor.run(anexo_port, -350)
            else: motor.stop(anexo_port)
            
        await runloop.sleep_ms(10)
    
    motor_pair.stop(motor_pair.PAIR_1)
    if anexo_port: motor.stop(anexo_port)

async def turn(target_yaw_deg, velocity=120):
    """Giro preciso usando o Giroscópio."""
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw_deg - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        
        if abs(error) < 0.5: break
            
        steering = 100 if error > 0 else -100
        current_vel = velocity if abs(error) > 15 else 50
        motor_pair.move(motor_pair.PAIR_1, steering, velocity=current_vel)
        await runloop.sleep_ms(10)
    motor_pair.stop(motor_pair.PAIR_1)

# --- DEFINIÇÃO DAS MISSÕES (0 a 6) ---

async def mission_0():
    print("Executando Diagnóstico...")
    for p in [port.A, port.B, port.C, port.D, port.E, port.F]:
        try:
            await motor.run_to_absolute_position(p, 0, 300)
        except: pass
    motion_sensor.reset_yaw(0)

async def mission_1():
    await move_straight(30, 400)
    await move_straight(30, -400)

async def mission_2():
    # Comparativo Giro vs Motores
    await move_straight(50, 300)
    print("Yaw Final: ", motion_sensor.tilt_angles()[0] * -0.1)

async def mission_3_4():
    # Quadrado de Precisão
    for i in range(4):
        await move_straight(30, 350)
        await turn(((i+1)*90)%360)

async def mission_5():
    # Trajeto com Retorno em Velocidade Máxima
    await move_straight(40, 350)
    await turn(60)
    await move_straight(30, 350)
    await runloop.sleep_ms(1000)
    await move_straight(30, -1000) # Volta Max
    await turn(0)
    await move_straight(40, -1000)

async def mission_6():
    # Retângulo 35x70 com Anexo
    lados = [35, 70, 35, 70]
    for i, dist in enumerate(lados):
        p_anexo = PORT_ATTACH if dist == 70 else None
        await move_straight(dist, 350, anexo_port=p_anexo)
        await turn(((i+1)*90)%360)

# --- NÚCLEO DO MENU SELETOR ---

async def main():
    motor_pair.pair(motor_pair.PAIR_1, PORT_LEFT, PORT_RIGHT)
    menu_index = 0
    max_missions = 6
    
    while True:
        light_matrix.write(str(menu_index))
        
        # Navegação do Menu
        if button.pressed(button.LEFT):
            menu_index = (menu_index - 1) % (max_missions + 1)
            await runloop.sleep_ms(250)
        elif button.pressed(button.RIGHT):
            menu_index = (menu_index + 1) % (max_missions + 1)
            await runloop.sleep_ms(250)
        
        # Iniciar Missão Selecionada (Usando o botão Bluetooth/Connect)
        if button.pressed(button.CONNECT):
            light_matrix.show_image(light_matrix.IMAGE_ARROW_N)
            print("\n>>> Iniciando Teste {}".format(menu_index))
            
            if menu_index == 0: await mission_0()
            elif menu_index == 1: await mission_1()
            elif menu_index == 2: await mission_2()
            elif menu_index == 3: await mission_3_4()
            elif menu_index == 4: await mission_3_4()
            elif menu_index == 5: await mission_5()
            elif menu_index == 6: await mission_6()
            
            print(">>> Teste {} Concluído!".format(menu_index))
            light_matrix.show_image(light_matrix.IMAGE_YES)
            await runloop.sleep_ms(1000)
            
        await runloop.sleep_ms(50)

runloop.run(main())
