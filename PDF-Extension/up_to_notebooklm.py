import asyncio
from playwright.async_api import async_playwright
import os

async def subir_pdf_a_notebooklm(ruta_archivo):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible
        context = await browser.new_context()

        # Usa sesión del usuario actual (ya logueado)
        page = await context.new_page()
        await page.goto("https://notebooklm.google.com", wait_until="load")

        # Espera a que cargue la interfaz y el usuario esté logueado
        await page.wait_for_timeout(3000)

        # Crea nuevo notebook
        await page.get_by_role("button", name="Crear nuevo").click()
        await page.wait_for_timeout(3000)

        # Click en “Agregar fuente”
        await page.get_by_text("Agregar fuente").click()
        await page.wait_for_timeout(2000)

        # Subir archivo PDF (input tipo file)
        input_file = await page.query_selector("input[type='file']")
        if input_file is not None and os.path.exists(ruta_archivo):
            await input_file.set_input_files(ruta_archivo)
            print("✅ Archivo subido correctamente.")
        else:
            print("❌ No se encontró input file o archivo inválido.")

        await page.wait_for_timeout(5000)
        await browser.close()

# Ejecutar directamente
if __name__ == "__main__":
    archivo_pdf = "salida_comprimido.pdf"  # Ajusta esta ruta
    asyncio.run(subir_pdf_a_notebooklm(archivo_pdf))
