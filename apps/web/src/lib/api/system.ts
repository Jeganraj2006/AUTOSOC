import { fetchApi } from "../api";

export async function purgeAllDatabaseRecords(): Promise<{ status: string; message: string }> {
  return fetchApi<{ status: string; message: string }>("/system/purge-all", {
    method: "POST",
  });
}

