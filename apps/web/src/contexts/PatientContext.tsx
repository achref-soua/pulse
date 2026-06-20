"use client";

import { createContext, useCallback, useContext, useState } from "react";

interface PatientContextValue {
  patientId: string | null;
  patientName: string | null;
  setPatient: (id: string, name: string) => void;
  clearPatient: () => void;
}

const Ctx = createContext<PatientContextValue | null>(null);

export function PatientContextProvider({ children }: { children: React.ReactNode }) {
  const [patientId, setPatientId] = useState<string | null>(null);
  const [patientName, setPatientName] = useState<string | null>(null);

  const setPatient = useCallback((id: string, name: string) => {
    setPatientId(id);
    setPatientName(name);
  }, []);

  const clearPatient = useCallback(() => {
    setPatientId(null);
    setPatientName(null);
  }, []);

  return (
    <Ctx.Provider value={{ patientId, patientName, setPatient, clearPatient }}>
      {children}
    </Ctx.Provider>
  );
}

export function usePatientContext() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("usePatientContext must be used inside PatientContextProvider");
  return ctx;
}
