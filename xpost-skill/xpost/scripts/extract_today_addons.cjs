const { execSync } = require('child_process');

function getTodayAddons() {
    const today = new Date().toISOString().split('T')[0];
    const logCommand = `git log --since="${today} 00:00:00" --until="${today} 23:59:59" --oneline -- docs/addons_data.json`;
    
    try {
        const logOutput = execSync(logCommand).toString().trim();
        if (!logOutput) {
            process.stdout.write(JSON.stringify({ message: "No commits found for today in docs/addons_data.json", addons: [] }));
            return;
        }

        const commits = logOutput.split('\n').map(line => line.split(' ')[0]);
        const addons = [];

        for (const commit of commits) {
            const diffCommand = `git diff ${commit}^..${commit} -- docs/addons_data.json`;
            const diffOutput = execSync(diffCommand).toString();
            
            const lines = diffOutput.split('\n');
            let currentAddon = null;

            for (const line of lines) {
                if (line.startsWith('+') && !line.startsWith('+++')) {
                    const content = line.substring(1).trim();
                    
                    if (content.includes('"nameEn":')) {
                        if (currentAddon && currentAddon.nameEn) {
                            addons.push(currentAddon);
                        }
                        currentAddon = {
                            nameEn: content.match(/"nameEn":\s*"(.*)",?/)?.[1]
                        };
                    } else if (currentAddon) {
                        if (content.includes('"descriptionJa":')) {
                            currentAddon.descriptionJa = content.match(/"descriptionJa":\s*"(.*)",?/)?.[1];
                        } else if (content.includes('"description":')) {
                            currentAddon.description = content.match(/"description":\s*"(.*)",?/)?.[1];
                        } else if (content.includes('"categoryJa":')) {
                            currentAddon.categoryJa = content.match(/"categoryJa":\s*"(.*)",?/)?.[1];
                        }
                    }
                } else if (!line.startsWith('+')) {
                    // Context line or minus line. If we were building an addon, check if it's finished.
                    // But in git diff, an addon might be split across hunks.
                    // However, for new additions, they are usually in one block.
                    // To be safe, we only push when we see a new nameEn or end of file.
                }
            }
            if (currentAddon && currentAddon.nameEn) {
                addons.push(currentAddon);
            }
        }

        // Deduplicate
        const seen = new Set();
        const uniqueAddons = addons.filter(a => {
            if (seen.has(a.nameEn)) return false;
            seen.add(a.nameEn);
            return true;
        });

        process.stdout.write(JSON.stringify({ addons: uniqueAddons }, null, 2));
    } catch (e) {
        process.stdout.write(JSON.stringify({ error: e.message, addons: [] }));
    }
}

getTodayAddons();
