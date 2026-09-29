import http from "k6/http";
import { check, sleep } from "k6";

// Usage:
//   k6 run load/k6-script.js
//   TARGET=http://localhost:8000 k6 run load/k6-script.js   (override the URL)
//
// Watch scaling while this runs:
//   kubectl get hpa -n civicpulse -w
const TARGET = __ENV.TARGET || "http://localhost:8000";

const complaints = [
  { text: "Burst water main flooding Street 12 since fajr, water entering ground floors", location: "Street 12, G-9" },
  { text: "Streetlight out on Main Boulevard for a week, very dark at night", location: "Main Boulevard" },
  { text: "Garbage not collected in our block for four days, smell is very bad", location: "Block C, F-10" },
  { text: "Pothole on the main road causing accidents daily", location: "Jinnah Road" },
  { text: "Electricity tripping every evening around 7pm in our sector", location: "Sector I-8" },
];

export const options = {
  scenarios: {
    ramping_load: {
      executor: "ramping-vus",
      startVUs: 1,
      stages: [
        { duration: "1m", target: 20 },   // ramp up — this is the part you time for HPA lag
        { duration: "3m", target: 20 },   // hold — gives the HPA time to react and scale out
        { duration: "1m", target: 0 },    // ramp down
      ],
    },
  },
};

export default function () {
  const complaint = complaints[Math.floor(Math.random() * complaints.length)];
  const res = http.post(`${TARGET}/api/complaints`, JSON.stringify(complaint), {
    headers: { "Content-Type": "application/json" },
  });
  check(res, {
    "status is 201 or 429": (r) => r.status === 201 || r.status === 429,
  });
  sleep(1);
}
