"use client";

import { redirect, useParams } from "next/navigation";

export default function Page() {
  const params = useParams();
  redirect(`/dashboard/server/${params.id}/overview`);
}
