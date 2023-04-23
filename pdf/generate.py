import asyncio
from pathlib import Path
from pydf import AsyncPydf

async def generate_async():
    apydf = AsyncPydf()

    async def gen(i):
        pdf_content = await apydf.generate_pdf('<h1>this is html</h1>')
        Path(f'output_{i:03}.pdf').write_bytes(pdf_content)

    coros = [gen(i) for i in range(50)]
    await asyncio.gather(*coros)

def main():
  loop = asyncio.get_event_loop()
  loop.run_until_complete(generate_async())
