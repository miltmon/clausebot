const express = require('express');
const redactMiddleware = require('./redactMiddleware');
const { callLLM, assertVendorContractGuard } = require('./llmClient');
const { uploadJSON } = require('./s3Storage');

const app = express();
app.use(express.json());
app.use(redactMiddleware);

// Guard vendor contract on boot
assertVendorContractGuard();

app.post('/extract', async (req, res) => {
  try {
    const { pageObj, selectors, task, schema, runId, outputPath } = req.body || {};
    const data = await callLLM({ task, schema, pageObj, selectors, runId });

    // Optional: store structured output to S3 (after schema validation in your code)
    if (outputPath) {
      const s3uri = await uploadJSON(outputPath, data);
      return res.json({ ok: true, data, s3: s3uri });
    }

    res.json({ ok: true, data });
  } catch (e) {
    const code = e.message === 'context_limit_exceeded' ? 400 : 500;
    res.status(code).json({ ok: false, error: e.message });
  }
});

app.listen(3000, () => console.log('OK on 3000'));
