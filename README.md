# TBC Ops System

## Overview

This project was built to solve a gap in day-to-day operations inside a Tire and Battery Center. The current system tracks work orders and sales, but it does not clearly track who was responsible for executing key steps like battery and wiper checks. Because work is logged under whoever is signed into the system, accountability becomes unclear and it is difficult to understand whether missed attachment sales come from customer demand or inconsistent execution.

This project introduces a simple system that assigns responsibility by shift, tracks execution with a lightweight checklist, and connects that execution back to performance.

---

## What This Solves

The current workflow captures results but not ownership. When attachment numbers are low, there is no clear way to determine:

- If the check was skipped  
- If the recommendation was never made  
- If responsibility was unclear due to shared logins  

This system creates a direct link between:

- The assigned associate  
- Whether the process was completed  
- How that day performed  

---

## System Components

### 1. Assignment Logic

A Python script reads a schedule and assigns:

- Primary opener  
- Primary closer  
- Backup (service advisor or team lead)  

Assignments are based on:

- Shift coverage windows  
- Role  
- Fairness rotation over time  

---

### 2. Daily Checklist

A printable checklist is generated for each day.

It includes:

- Assigned opener and closer  
- Backup support  
- A single completion mark per role  

The checklist is designed to be simple enough to use during a shift while still creating a clear accountability record.

---

### 3. Execution Tracking

The checklist does not replace the work order system. Instead, it fills the gap by tracking whether the expected process was actually followed under assigned ownership.

This allows performance to be evaluated based on execution, not just outcome.

---

### 4. Decision Model

A simple model is included to show how changes in execution impact:

- Attachment rates  
- Time per interaction  
- Overall revenue  

This turns the system from a tracking tool into a way to test and understand operational changes.

---

## How It Works

- Input schedule data  
- Run assignment script  
- Generate daily checklist  
- Print and use during shift  
- Compare execution with performance  

---

## Why It Works

The system does not rely on increased effort. It works by:

- Embedding responsibility into the schedule  
- Making ownership visible  
- Simplifying tracking to a single action  
- Creating a clear connection between process and results  

---

## Project Structure
# tbc-ops-system/
│
├── proposal/
├── scheduler/
├── checklist/
├── model/
├── workflow/
├── data/
└── README.md

---

## Goal

The goal is not to add complexity, but to remove ambiguity.

By turning a loosely followed process into a structured and visible system, this project makes it easier to understand performance, correct breakdowns, and improve consistency without slowing down operations.
