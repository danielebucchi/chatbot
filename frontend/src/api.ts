import axios from 'axios';

const BASE_URL = 'http://localhost:7373';

export async function askQuestion(question: string, files: File[]) {
  const formData = new FormData();
  formData.append('question', question);
  files.forEach(file => formData.append('files', file));

  const res = await axios.post(`${BASE_URL}/ask`, formData);

  const claimsRaw = res.data["claims"];
  const claims: Claim[] = Object.entries(claimsRaw).map(([id, value]) => ({
    id,
    text: value.text,
    weight: value.weight
  }));

  const maxWeight = Math.max(...claims.map(c => c.weight));
  const topClaims = claims.filter(c => c.weight === maxWeight);

  return topClaims;
}


export async function submitClaim(question: string, files: File[], claim_id: string) {
  const formData = new FormData();
  formData.append('question', question);
  formData.append('claim_id', claim_id);
  files.forEach(file => formData.append('files', file));

  const res = await axios.post(`${BASE_URL}/claim`, formData);
  return res.data;
}