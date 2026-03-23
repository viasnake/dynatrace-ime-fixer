import fs from "node:fs";

function main() {
  const version = process.argv[2];

  if (!version) {
    console.error("Usage: node scripts/sync_manifest_version.mjs <version>");
    process.exit(1);
  }

  const manifestPath = "manifest.json";
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  manifest.version = version;
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");

  console.log(`Updated manifest version to ${version}`);
}

main();
