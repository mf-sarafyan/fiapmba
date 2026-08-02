"""
Smoke test das ferramentas de dados, sem subir o ADK.

Valida a camada mais fragil do sistema - a integracao HTTP - isoladamente.
Se este script falhar, o problema e de rede, token ou API; nao do agente.

Uso (a partir do diretorio PAI de quantum_finance_advisor):
    python -m quantum_finance_advisor.scripts.smoke_test_tools
"""

import json

from ..tools.b3_tools import (
    consultar_cotacao_b3,
    consultar_fundamentos_b3,
    consultar_indicadores_macro,
)


def _mostrar(titulo: str, resultado: dict) -> bool:
    ok = resultado.get("status") == "success"
    marcador = "OK  " if ok else "FALHA"
    print(f"\n[{marcador}] {titulo}")
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str)[:900])
    return ok


def main() -> None:
    resultados = [
        _mostrar("Cotacao PETR4", consultar_cotacao_b3("PETR4")),
        _mostrar("Fundamentos ITUB4", consultar_fundamentos_b3("ITUB4")),
        _mostrar("Indicadores macro (Selic/IPCA)", consultar_indicadores_macro()),
        _mostrar("Ticker invalido (deve falhar)", consultar_cotacao_b3("XXXX0")),
    ]
    esperado = [True, True, True, False]
    print("\n" + "=" * 60)
    print(f"Resultado: {sum(r == e for r, e in zip(resultados, esperado))}/4 conforme esperado")


if __name__ == "__main__":
    main()
