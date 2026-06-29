import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAppStore = create(
  persist(
    (set, get) => ({
      // ── Active dataset ────────────────────────────────────────────────────
      activeDatasetId: null,
      activeDataset: null,
      setActiveDataset: (dataset) => set({ activeDatasetId: dataset?.id || null, activeDataset: dataset }),

      // ── Active candidate ─────────────────────────────────────────────────
      activeCandidateId: null,
      setActiveCandidateId: (id) => set({ activeCandidateId: id }),

      // ── Processing jobs (in-memory) ───────────────────────────────────────
      jobs: {},
      setJobStatus: (jobId, status) => set((s) => ({
        jobs: { ...s.jobs, [jobId]: { ...s.jobs[jobId], ...status } },
      })),

      // ── Sidebar state ─────────────────────────────────────────────────────
      sidebarCollapsed: false,
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),

      // ── Pipeline results cache ────────────────────────────────────────────
      preprocessingResult: null,
      setPreprocessingResult: (r) => set({ preprocessingResult: r }),

      detectionResult: null,
      setDetectionResult: (r) => set({ detectionResult: r }),

      validationResults: {},
      setValidationResult: (candidateId, r) => set((s) => ({
        validationResults: { ...s.validationResults, [candidateId]: r },
      })),

      characterizationResults: {},
      setCharacterizationResult: (candidateId, r) => set((s) => ({
        characterizationResults: { ...s.characterizationResults, [candidateId]: r },
      })),

      // ── Reset ────────────────────────────────────────────────────────────
      reset: () => set({
        activeDatasetId: null,
        activeDataset: null,
        activeCandidateId: null,
        preprocessingResult: null,
        detectionResult: null,
        validationResults: {},
        characterizationResults: {},
      }),
    }),
    {
      name: 'horizon-app-store',
      partialize: (state) => ({
        activeDatasetId: state.activeDatasetId,
        activeDataset: state.activeDataset,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
)
