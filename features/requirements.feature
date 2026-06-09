# -*- coding: utf-8 -*-
Feature: Gestion de requerimientos SITESIGO

  Background:
    Given que el primer usuario es super_admin con email "sa@req.com" y password "sa123"
    And que el super_admin crea el proyecto "SITESIGO"
    And que existe un admin en el proyecto con email "admin@test.com" y password "admin123"

  Scenario: Funcionario registra requerimiento valido
    Given que estoy autenticado como admin
    When creo un requerimiento con titulo "Error en MGA" y descripcion "El indicador no guarda el valor" y tipo "Bug" y prioridad "Alta"
    Then el requerimiento se crea con estado "Nuevo"
    And la respuesta tiene codigo 201

  Scenario: No se puede crear requerimiento sin descripcion
    Given que estoy autenticado como admin
    When creo un requerimiento con titulo "Error en MGA" y descripcion "" y tipo "Bug" y prioridad "Alta"
    Then la respuesta tiene codigo 422

  Scenario: Admin cambia estado exitosamente
    Given que estoy autenticado como admin
    And existe un requerimiento en estado "Nuevo"
    When el admin cambia el estado a "En analisis"
    Then el requerimiento tiene estado "En analisis"
    And la respuesta tiene codigo 200

  Scenario: Funcionario no puede cambiar estado
    Given que existe un usuario funcionario registrado con email "func@test.com" y password "func123" y rol "funcionario"
    And existe un requerimiento en estado "Nuevo"
    And que estoy autenticado como funcionario
    When intento cambiar el estado a "En analisis"
    Then la respuesta tiene codigo 403

  Scenario: Requerimiento cerrado no puede cambiar estado
    Given que estoy autenticado como admin
    And existe un requerimiento en estado "Nuevo"
    When el admin cambia el estado a "Cerrado"
    And el admin intenta cambiar el estado a "En analisis"
    Then la respuesta tiene codigo 422

  Scenario: Admin archiva un requerimiento
    Given que estoy autenticado como admin
    And existe un requerimiento en estado "Nuevo"
    When el admin archiva el requerimiento
    Then la respuesta tiene codigo 200
    And el requerimiento tiene estado "Archivado"
