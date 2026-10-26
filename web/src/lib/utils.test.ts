import { cn } from "./utils";

// Minimal component/unit test verifying utility function behavior
if (cn("px-2", "py-1") !== "px-2 py-1") {
    throw new Error("cn failed to concatenate class names");
}
if (cn("p-4", false && "hidden", undefined, "bg-white") !== "p-4 bg-white") {
    throw new Error("cn failed to filter falsy values");
}
