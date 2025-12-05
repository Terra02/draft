# test_api_endpoints.py
import asyncio
import httpx
import json

async def test_api():
    base_url = "http://localhost:8000"  # или "http://api:8000" если в Docker
    
    async with httpx.AsyncClient() as client:
        print("🔍 Тестируем endpoints API...")
        
        # 1. Проверяем корневой endpoint
        try:
            response = await client.get(f"{base_url}/")
            print(f"GET / - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Не могу подключиться к {base_url}: {e}")
            return
        
        # 2. Проверяем OpenAPI docs
        try:
            response = await client.get(f"{base_url}/docs")
            print(f"GET /docs - Status: {response.status_code}")
        except:
            print("❌ /docs недоступен")
        
        # 3. Проверяем создание пользователя
        test_data = {
            "telegram_id": "5206838876",
            "username": "test_user_api",
            "first_name": "Test",
            "last_name": "User"
        }
        
        print(f"\n📤 Пробуем POST /api/v1/users с данными: {json.dumps(test_data)}")
        
        try:
            # Пробуем оба варианта (со слэшом и без)
            for endpoint in ["/api/v1/users", "/api/v1/users/"]:
                print(f"\n🔗 Пробуем endpoint: {endpoint}")
                response = await client.post(
                    f"{base_url}{endpoint}",
                    json=test_data,
                    timeout=10.0
                )
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 201 or response.status_code == 200:
                    print(f"✅ Успех с endpoint: {endpoint}")
                    break
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        # 4. Проверяем поиск пользователя
        print(f"\n🔍 Пробуем GET /api/v1/users/telegram/5206838876")
        try:
            response = await client.get(f"{base_url}/api/v1/users/telegram/5206838876")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())