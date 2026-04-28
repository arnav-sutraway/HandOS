const commands = [
  ["Start runtime", "python -m handos"],
  ["Run headless", "python -m handos --no-preview"],
  ["Tune pinch hold", "python -m handos --pinch-click-hold-seconds 1.0"],
  ["Lower capture load", "python -m handos --width 640 --height 480"],
];

export function CLIReference() {
  return (
    <div className="cli-reference">
      {commands.map(([label, command]) => (
        <div className="cli-row" key={label}>
          <span>{label}</span>
          <code>{command}</code>
        </div>
      ))}
    </div>
  );
}
