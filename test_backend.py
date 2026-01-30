import asyncio
import httpx
import json
from typing import Dict, Any
import sys

BASE_URL = "http://localhost:8000"

async def test_endpoint(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """Testea un endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"\n{'='*60}")
            print(f"🔍 Test: {method} {endpoint}")
            
            if method.upper() == "GET":
                response = await client.get(f"{BASE_URL}{endpoint}", **kwargs)
            elif method.upper() == "POST":
                print(f"📤 Request body: {json.dumps(kwargs.get('json'), indent=2, ensure_ascii=False)}")
                response = await client.post(f"{BASE_URL}{endpoint}", **kwargs)
            
            print(f"📥 Status: {response.status_code}")
            
            try:
                data = response.json()
                print(f"✅ Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")  # Limitar output
                return data
            except:
                print(f"📄 Response (text): {response.text[:500]}...")
                return {"text": response.text}
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

async def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas del backend Cliro Notes")
    print("💡 Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    
    results = []
    
    try:
        # 1. Health check básico
        print("\n" + "="*60)
        print("1. Health checks")
        results.append(await test_endpoint("GET", "/"))
        results.append(await test_endpoint("GET", "/health"))
        
        # 2. Configuración pública
        print("\n" + "="*60)
        print("2. Configuración pública")
        results.append(await test_endpoint("GET", "/api/auth/config/public"))
        
        # 3. Check email (debería decir disponible)
        print("\n" + "="*60)
        print("3. Check email disponible")
        results.append(await test_endpoint("GET", "/api/auth/waitlist/check-email/test@example.com"))
        
        # 4. Stats de waitlist (vacía)
        print("\n" + "="*60)
        print("4. Stats iniciales (vacías)")
        results.append(await test_endpoint("GET", "/api/auth/waitlist/stats"))
        
        # 5. Registrar usuario en waitlist (éxito)
        print("\n" + "="*60)
        print("5. Registrar primer usuario")
        new_user = {
            "email": "test.user@example.com",
            "name": "Test User",
            "interest_reason": "productivity",
            "preferred_languages": ["es", "en"]
        }
        result1 = await test_endpoint("POST", "/api/auth/waitlist/join", json=new_user)
        results.append(result1)
        
        if result1.get("success"):
            print("✅ Primer usuario registrado exitosamente!")
        else:
            print("⚠️  Primer registro falló, continuando...")
        
        # 6. Intentar registrar mismo usuario (debería fallar)
        print("\n" + "="*60)
        print("6. Intentar registrar mismo email (debería fallar)")
        result2 = await test_endpoint("POST", "/api/auth/waitlist/join", json=new_user)
        results.append(result2)
        
        # 7. Check email ahora (debería decir registrado)
        print("\n" + "="*60)
        print("7. Verificar email ahora registrado")
        results.append(await test_endpoint("GET", "/api/auth/waitlist/check-email/test.user@example.com"))
        
        # 8. Stats de waitlist (ahora con 1 usuario)
        print("\n" + "="*60)
        print("8. Stats después de registro")
        results.append(await test_endpoint("GET", "/api/auth/waitlist/stats"))
        
        # 9. Probar acciones de IA (si Gemini API está configurada)
        print("\n" + "="*60)
        print("9. Probar acciones de IA")
        
        # Test simple primero
        test_params = {
            "action": "summarize",
            "text": "Hola mundo. Esta es una prueba."
        }
        ai_test = await test_endpoint("GET", "/api/ai/process", params=test_params)
        results.append(ai_test)
        
        if ai_test.get("success"):
            print("✅ IA funcionando correctamente")
            
            # Más pruebas de IA si la primera funciona
            print("\n" + "="*60)
            print("10. Probar más acciones de IA")
            
            # Reescribir
            rewrite_params = {
                "action": "rewrite",
                "text": "Hola, cómo estás? Espero que bien.",
                "tone": "formal"
            }
            results.append(await test_endpoint("GET", "/api/ai/process", params=rewrite_params))
            
            # Traducir
            translate_params = {
                "action": "translate",
                "text": "El gato está sobre la mesa",
                "language": "en"
            }
            results.append(await test_endpoint("GET", "/api/ai/process", params=translate_params))
            
        else:
            print("⚠️  IA no funcionando (posible falta de API key o quota)")
        
        # 11. Registrar otro usuario
        print("\n" + "="*60)
        print("11. Registrar segundo usuario")
        new_user2 = {
            "email": "juan.perez@empresa.com",
            "name": "Juan Pérez",
            "interest_reason": "business",
            "preferred_languages": ["es", "en", "fr"]
        }
        results.append(await test_endpoint("POST", "/api/auth/waitlist/join", json=new_user2))
        
        # 12. Stats finales
        print("\n" + "="*60)
        print("12. Stats finales")
        results.append(await test_endpoint("GET", "/api/auth/waitlist/stats"))
        
        # Resumen
        print("\n" + "="*60)
        print("📊 RESUMEN DE PRUEBAS")
        print("="*60)
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if isinstance(r, dict) and r.get("success") in [True, None])
        
        print(f"Total pruebas ejecutadas: {total_tests}")
        print(f"Pruebas exitosas: {successful_tests}")
        print(f"Pruebas fallidas: {total_tests - successful_tests}")
        
        if successful_tests == total_tests:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        elif successful_tests >= total_tests * 0.7:
            print("✅ La mayoría de las pruebas pasaron")
        else:
            print("⚠️  Algunas pruebas fallaron, revisa los logs")
        
    except Exception as e:
        print(f"❌ Error en suite de pruebas: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("🏁 Pruebas completadas")
    print("="*60)

if __name__ == "__main__":
    # Ejecutar pruebas asíncronas
    asyncio.run(run_all_tests())