# Estruturas de Dados

Aplicação Pygame integrada a uma DLL C por `ctypes`, com Fila, Pilha, Lista encadeada e Histórico.

## Ambiente validado

- Windows x64
- Python 3.13.7
- Pygame 2.6.1
- CMake 4.x
- MinGW GCC 16.1.0

## Instalação

No PowerShell, a partir da raiz do projeto:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Compilar a DLL

A DLL esperada fica em `native/bin/x64/datastructures.dll`.

Em caminhos sem acentos:

```powershell
cmake -S native -B native/build -G "MinGW Makefiles"
cmake --build native/build --config Release
```

Se o caminho do projeto tiver acentos, como `Área de Trabalho`, o MinGW pode reinterpretar o caminho durante o build. Nesse caso, use temporariamente uma unidade virtual sem acentos:

```powershell
subst X: "C:\Users\SEU_USUARIO\OneDrive\Área de Trabalho\trabalho python"
cmake -S X:\native -B X:\native\build_x -G "MinGW Makefiles"
cmake --build X:\native\build_x --config Release
subst X: /d
```

A DLL será escrita na pasta real `native/bin/x64`.

## Executar

```powershell
.venv\Scripts\python.exe main.py
```

A interface começa em português e usa a DLL como fonte oficial dos dados. Sem a DLL, a aplicação informa o erro de inicialização em vez de simular estruturas.

## Testes

Atualmente, a validação é feita executando a aplicação após compilar a DLL. A pasta `tests/` pode ser adicionada posteriormente para automatizar os testes de integração.

## Organização

- `native/include/ds_api.h`: contrato ABI público.
- `native/src/ds_api_all.c`: implementação C das estruturas e do histórico usada pelo build.
- `native/bin/x64/datastructures.dll`: biblioteca compilada, gerada localmente e ignorada pelo Git.
- `python_app/native_api.py`: fronteira `ctypes`.
- `python_app/controller.py`: coordenação e cache de apresentação.
- `python_app/visual_ui.py`: interface Pygame.
