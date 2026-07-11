'use client';

import { createContext, useContext, ReactNode } from 'react';

const DrawnNumbersContext = createContext<Set<number> | null>(null);

export function DrawnNumbersProvider({ numeros, children }: { numeros: number[]; children: ReactNode }) {
  return (
    <DrawnNumbersContext.Provider value={new Set(numeros)}>
      {children}
    </DrawnNumbersContext.Provider>
  );
}

export function useDrawnNumbers(): Set<number> | null {
  return useContext(DrawnNumbersContext);
}
