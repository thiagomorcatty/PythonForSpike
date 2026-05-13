import motor
import runloop
from hub import port, motion_sensor
import utime

async def main():
    print("--- Teste 0: Diagnóstico e Reset Geral ---")
    
    # Lista de todas as portas do Hub SPIKE Prime
    todas_as_portas = [
        ('A', port.A),
        ('B', port.B),
        ('C', port.C),
        ('D', port.D),
        ('E', port.E),
        ('F', port.F)
    ]
    
    motores_encontrados = []
    
    print("\n1. Verificando conexões...")
    for nome, p in todas_as_portas:
        try:
            # Tenta ler a posição absoluta. Se falhar, não há motor nesta porta.
            pos = motor.absolute_position(p)
            print("  [OK] Motor detectado na Porta {} (Posição atual: {}°)".format(nome, pos))
            motores_encontrados.append(p)
        except Exception:
            # Nenhuma ação se não houver motor
            pass
            
    if not motores_encontrados:
        print("  [!] Nenhum motor detectado. Verifique as conexões.")
        return

    print("\n2. Resetando motores para a posição zero...")
    for p in motores_encontrados:
        # Move cada motor para a posição absoluta 0 com velocidade segura
        await motor.run_to_absolute_position(p, 0, 300)
    
    print("\n3. Resetando Giroscópio...")
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(1000)
    yaw = motion_sensor.tilt_angles()[0] / 10.0
    print("  [OK] Yaw resetado para: {}°".format(yaw))

    print("\n--- Diagnóstico Concluído ---")
    print("Todos os motores alinhados no 0 absoluto.")

runloop.run(main())
