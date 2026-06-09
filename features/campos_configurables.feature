# -*- coding: utf-8 -*-
Feature: Campos y estados configurables por proyecto

  Background:
    Given que el primer usuario es super_admin con email "sa@test.com" y password "sa123"
    And que el super_admin crea el proyecto "SITESIGO"
    And que existe un admin en el proyecto con email "admin@test.com" y password "admin123"

  Scenario: Super-Admin configura campo de tipo texto (RN-20, RN-21)
    Given que estoy autenticado como super_admin
    When creo un campo con nombre "Observaciones" y clave "observaciones" y tipo "texto"
    Then la respuesta tiene codigo 201
    And el campo tiene tipo "texto"

  Scenario: Super-Admin configura campo de tipo lista con opciones (RN-21)
    Given que estoy autenticado como super_admin
    When creo un campo de lista con nombre "Proceso" y clave "proceso" y opciones "Seguimiento Fisico,Informes"
    Then la respuesta tiene codigo 201
    And el campo tiene tipo "lista"

  Scenario: Campo de tipo lista sin opciones es rechazado (RN-21)
    Given que estoy autenticado como super_admin
    When creo un campo de lista sin opciones con nombre "Vacio" y clave "vacio"
    Then la respuesta tiene codigo 422

  Scenario: Admin no puede configurar campos (RN-20)
    Given que estoy autenticado como admin en el proyecto
    When intento crear un campo con nombre "X" y clave "x" y tipo "texto"
    Then la respuesta tiene codigo 403

  Scenario: Super-Admin configura estado de proyecto (RN-23, RN-24)
    Given que estoy autenticado como super_admin
    When creo un estado con nombre "En Espera" y color "#94a3b8"
    Then la respuesta tiene codigo 201
    And el estado tiene nombre "En Espera"
    And el estado no es terminal

  Scenario: Super-Admin configura estado terminal (RN-23, RN-24)
    Given que estoy autenticado como super_admin
    When creo un estado terminal con nombre "Entregado" y color "#10b981"
    Then la respuesta tiene codigo 201
    And el estado es terminal

  Scenario: Admin no puede configurar estados (RN-23)
    Given que estoy autenticado como admin en el proyecto
    When intento crear un estado con nombre "X" y color "#ffffff"
    Then la respuesta tiene codigo 403

  Scenario: Calculo de dias habiles excluye festivos colombianos (RN-22)
    Given que estoy autenticado como super_admin
    When calculo dias habiles entre "2026-01-01" y "2026-01-05"
    Then los dias habiles son 1

  Scenario: Calculo de dias habiles en semana normal (RN-22)
    Given que estoy autenticado como super_admin
    When calculo dias habiles entre "2026-01-05" y "2026-01-12"
    Then los dias habiles son 5
