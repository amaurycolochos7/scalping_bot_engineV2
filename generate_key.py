#!/usr/bin/env python
"""
Script CLI para generar keys de acceso
Ejecutar desde el servidor: python generate_key.py
"""
import sys
from pathlib import Path

# Agregar directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from keys_manager import generate_key, DURATIONS, get_all_keys


def show_menu():
    """Muestra el menú de opciones"""
    print("\n" + "=" * 50)
    print("🔑 GENERADOR DE KEYS DE ACCESO")
    print("=" * 50)
    print("\nSeleccione la duración de la key:\n")
    
    for num, (label, hours) in DURATIONS.items():
        print(f"  {num}. {label}")
    
    print(f"\n  0. Ver todas las keys")
    print(f"  q. Salir")
    print()


def show_all_keys():
    """Muestra todas las keys generadas"""
    keys = get_all_keys()
    
    if not keys:
        print("\n📭 No hay keys generadas aún.\n")
        return
    
    print("\n" + "=" * 80)
    print("📋 LISTA DE KEYS")
    print("=" * 80)
    print(f"{'KEY':<22} {'DURACIÓN':<12} {'ESTADO':<10} {'CREADA':<20} {'USUARIO'}")
    print("-" * 80)
    
    for k in keys:
        duration_label = f"{k['duration_hours']}h"
        if k['duration_hours'] >= 720:
            duration_label = f"{k['duration_hours'] // 720} mes(es)"
        elif k['duration_hours'] >= 24:
            duration_label = f"{k['duration_hours'] // 24} día(s)"
        
        user = str(k['user_id']) if k['user_id'] else "-"
        created = k['created_at'][:16] if k['created_at'] else "-"
        
        print(f"{k['key']:<22} {duration_label:<12} {k['status']:<10} {created:<20} {user}")
    
    print("-" * 80)
    print(f"Total: {len(keys)} keys\n")


def main():
    """Función principal del CLI"""
    while True:
        show_menu()
        
        try:
            choice = input("Opción: ").strip().lower()
            
            if choice == 'q':
                print("\n👋 ¡Hasta luego!\n")
                break
            
            if choice == '0':
                show_all_keys()
                input("Presiona Enter para continuar...")
                continue
            
            option = int(choice)
            
            if option not in DURATIONS:
                print("\n❌ Opción inválida. Por favor selecciona 1-7.\n")
                continue
            
            # Generar key
            key, duration_label, duration_hours = generate_key(option)
            
            print("\n" + "=" * 50)
            print("✅ KEY GENERADA EXITOSAMENTE")
            print("=" * 50)
            print(f"\n🔑 Key: {key}")
            print(f"⏱️  Duración: {duration_label}")
            print(f"\n📝 Esta key es válida hasta que sea activada.")
            print("   El tiempo empieza a correr cuando un usuario")
            print("   la ingrese en el bot.")
            print("=" * 50 + "\n")
            
            # Preguntar si generar otra
            another = input("¿Generar otra key? (s/n): ").strip().lower()
            if another != 's':
                print("\n👋 ¡Hasta luego!\n")
                break
                
        except ValueError:
            print("\n❌ Por favor ingresa un número válido.\n")
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
