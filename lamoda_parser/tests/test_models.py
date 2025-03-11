import g4f
import asyncio
import time
from typing import List, Dict

class ProviderTester:
    def __init__(self):
        # Получаем все доступные провайдеры
        self.all_providers = [
            provider for provider in g4f.Provider.__providers__ 
            if provider.working
        ]
        self.working_providers = []
        self.test_message = "Generate a short greeting"
        
    async def test_provider(self, provider, timeout=15) -> Dict:
        start_time = time.time()
        try:
            response = await asyncio.wait_for(
                g4f.ChatCompletion.create_async(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": self.test_message}],
                    provider=provider
                ),
                timeout=timeout
            )
            execution_time = time.time() - start_time
            return {
                "success": True,
                "provider": provider.__name__,
                "response": response,
                "time": execution_time
            }
        except Exception as e:
            return {
                "success": False,
                "provider": provider.__name__,
                "error": str(e)
            }

    async def test_all_providers(self):
        print(f"Testing {len(self.all_providers)} providers...")
        
        tasks = [self.test_provider(provider) for provider in self.all_providers]
        results = await asyncio.gather(*tasks)
        
        # Анализируем результаты
        for result in results:
            if result["success"]:
                self.working_providers.append({
                    "name": result["provider"],
                    "response": result["response"],
                    "time": result["time"]
                })
                print(f"✅ {result['provider']} - {result['time']:.2f}s")
            else:
                print(f"❌ {result['provider']} - {result['error']}")

        # Сортируем по времени ответа
        self.working_providers.sort(key=lambda x: x["time"])
        
        return self.working_providers

async def main():
    tester = ProviderTester()
    working = await tester.test_all_providers()
    
    print("\n=== Working Providers ===")
    for provider in working:
        print(f"\nProvider: {provider['name']}")
        print(f"Response time: {provider['time']:.2f}s")
        print(f"Response: {provider['response'][:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
