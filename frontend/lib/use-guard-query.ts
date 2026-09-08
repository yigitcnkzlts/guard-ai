"use client";

import useSWR from "swr";

import { GuardApiError } from "@/lib/api";

export function useGuardQuery<T>(key: string, loader: () => Promise<T>) {
  const { data, error, isLoading, mutate } = useSWR<T>(key, loader, {
    revalidateOnFocus: false,
    shouldRetryOnError: false,
  });

  const message = error
    ? error instanceof GuardApiError
      ? error.message
      : "GUARD backend is currently unavailable."
    : null;

  return {
    data: data ?? null,
    loading: isLoading,
    error: message,
    reload: mutate,
  };
}
