const fs = require('fs');
const FormData = require('form-data');
const fetch = require('node-fetch');

async function testCCRWorkflow() {
    const API_URL = 'http://localhost:8000';
    
    console.log('🔍 Testing CCR Analysis Workflow');
    console.log('API URL:', API_URL);
    
    try {
        // Step 1: Test health check
        console.log('\n1. Testing health check...');
        const healthResponse = await fetch(`${API_URL}/health`);
        const healthData = await healthResponse.json();
        console.log('✅ Health check:', healthData);
        
        // Step 2: Upload test image
        console.log('\n2. Testing image upload...');
        const formData = new FormData();
        
        // Create a simple test image buffer
        const testImageBuffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64');
        formData.append('files', testImageBuffer, {
            filename: 'test_chart.png',
            contentType: 'image/png'
        });
        
        const uploadResponse = await fetch(`${API_URL}/upload-images`, {
            method: 'POST',
            body: formData
        });
        
        console.log('Upload response status:', uploadResponse.status);
        console.log('Upload response headers:', Object.fromEntries(uploadResponse.headers));
        
        if (!uploadResponse.ok) {
            const errorText = await uploadResponse.text();
            console.error('❌ Upload failed:', errorText);
            return;
        }
        
        const uploadResult = await uploadResponse.json();
        console.log('✅ Upload successful:', uploadResult);
        
        // Step 3: Configure cropping
        console.log('\n3. Testing cropping configuration...');
        const cropConfig = { rows: 2, cols: 3, enabled: true };
        
        const configResponse = await fetch(`${API_URL}/configure-cropping`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cropConfig)
        });
        
        console.log('Config response status:', configResponse.status);
        
        if (!configResponse.ok) {
            const errorText = await configResponse.text();
            console.error('❌ Configuration failed:', errorText);
            return;
        }
        
        const configResult = await configResponse.json();
        console.log('✅ Configuration successful:', configResult);
        
        // Step 4: Analyze
        console.log('\n4. Testing analysis...');
        const analyzeResponse = await fetch(`${API_URL}/analyze`, {
            method: 'POST'
        });
        
        console.log('Analysis response status:', analyzeResponse.status);
        
        if (!analyzeResponse.ok) {
            const errorText = await analyzeResponse.text();
            console.error('❌ Analysis failed:', errorText);
            return;
        }
        
        const analysisResult = await analyzeResponse.json();
        console.log('✅ Analysis successful:', JSON.stringify(analysisResult, null, 2));
        
        // Step 5: Test download
        console.log('\n5. Testing report download...');
        const downloadResponse = await fetch(`${API_URL}/download-report`);
        
        console.log('Download response status:', downloadResponse.status);
        console.log('Download response headers:', Object.fromEntries(downloadResponse.headers));
        
        if (!downloadResponse.ok) {
            const errorText = await downloadResponse.text();
            console.error('❌ Download failed:', errorText);
            return;
        }
        
        console.log('✅ Download successful - Content-Type:', downloadResponse.headers.get('content-type'));
        
        console.log('\n🎉 All CCR workflow tests passed!');
        
    } catch (error) {
        console.error('💥 Test failed:', error.message);
        console.error('Error details:', error);
    }
}

testCCRWorkflow();