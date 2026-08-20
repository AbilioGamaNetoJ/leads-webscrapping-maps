# Feature: Catálogo de Tipos de Negócio

| Field | Value |
|---|---|
| **ID** | `business-type-catalog` |
| **Status** | Done |
| **Priority** | High |
| **Effort** | M |
| **Created** | 2026-08-20 |

## Summary

Disponibilizar os 92 nichos enviados pelo time comercial no seletor de tipo de
negócio, sem enviar identificadores internos inválidos à Google Places API.

## Requirements

### R1 — Catálogo completo

O catálogo deve conter cada nicho e todos os termos fornecidos para ele.

### R2 — Busca compatível com Places

Os termos de um nicho devem orientar buscas textuais. `includedType` só pode
receber valores oficiais suportados pela Places API.

### R3 — Rastreabilidade do lead

O nicho selecionado deve ser salvo junto ao lead e estar disponível no
histórico e no XLSX.
